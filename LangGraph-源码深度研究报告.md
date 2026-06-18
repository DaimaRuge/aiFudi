# LangGraph 源码深度研究报告

> 基于 [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) 代码库分析  
> 版本: 1.1.9 | 分析日期: 2026-04-24

---

## 1. 项目概述

### 1.1 项目定位

LangGraph 是一个**低级别的有状态 Agent 编排框架**，用于构建、管理和部署长期运行、有状态的多智能体应用。它由 LangChain 团队开发，解决了 LLM 应用中**状态管理、流程控制、持久化和人机协作**等核心问题。

核心能力：
- **有状态图执行**：基于 Pregel/BSP 模型的图计算引擎
- **Human-in-the-loop**：原生支持中断/恢复机制
- **持久化检查点**：支持时间旅行调试和断点续跑
- **流式处理**：多种流式模式（values、updates、messages、events、custom）
- **子图组合**：支持图嵌套和并行执行
- **生产部署**：通过 LangGraph Platform 提供托管部署方案

### 1.2 社区数据

- **许可证**: MIT
- **版本**: 1.1.9（当前稳定版），处于 Production/Stable 状态
- **Python 支持**: 3.10 - 3.13
- **最近活跃**: 2026-04-22 仍有提交（#7585）
- **依赖**: langchain-core >= 1.3.0, pydantic >= 2.7.4, xxhash >= 3.5.0
- **下游依赖库**: langgraph-checkpoint, langgraph-sdk, langgraph-prebuilt

### 1.3 版本历史

从代码中可以看到重要的演进：
- `MessageGraph`（纯消息图）已弃用，统一到 `StateGraph`
- `config_schema` 弃用，改用 `context_schema`
- v1.0 引入了 `Runtime`、`Command`、`entrypoint` 函数式 API
- v2 流式格式（`StreamPart` typed dicts）正在推广

---

## 2. 技术架构分析

### 2.1 代码目录结构

```
libs/
├── langgraph/           # 核心库
│   ├── channels/        # 通道实现（状态存储抽象）
│   │   ├── base.py          # BaseChannel 抽象基类
│   │   ├── last_value.py    # LastValue / LastValueAfterFinish
│   │   ├── topic.py         # Topic（PubSub 多值通道）
│   │   ├── binop.py         # BinaryOperatorAggregate
│   │   ├── ephemeral_value.py  # EphemeralValue（输入专用）
│   │   ├── any_value.py     # AnyValue
│   │   ├── named_barrier_value.py  # NamedBarrierValue
│   │   └── untracked_value.py  # UntrackedValue
│   ├── func/            # 函数式 API（@task, @entrypoint）
│   ├── graph/           # 图构建 API
│   │   ├── state.py         # StateGraph / CompiledStateGraph（1752 行）
│   │   ├── message.py       # add_messages / MessagesState
│   │   ├── _node.py         # StateNode / StateNodeSpec
│   │   ├── _branch.py       # BranchSpec（条件边）
│   │   └── ui.py            # 图可视化
│   ├── pregel/          # Pregel 执行引擎
│   │   ├── main.py          # Pregel 类（3773 行，核心入口）
│   │   ├── _algo.py         # 核心算法（1258 行）
│   │   ├── _loop.py         # 执行循环（1512 行）
│   │   ├── _retry.py        # 重试机制
│   │   ├── _executor.py     # 执行器
│   │   ├── _read.py         # 节点读取（ChannelRead / PregelNode）
│   │   ├── _write.py        # 节点写入（ChannelWrite）
│   │   ├── _checkpoint.py   # 检查点逻辑
│   │   ├── _call.py         # 调用工具
│   │   ├── _io.py           # I/O 读写
│   │   ├── _validate.py     # 图验证
│   │   ├── _draw.py         # 图绘制
│   │   ├── _runner.py       # 运行器
│   │   ├── _log.py          # 日志
│   │   ├── _utils.py        # 工具函数
│   │   ├── _config.py       # 配置处理
│   │   ├── _messages.py     # 消息流处理
│   │   ├── protocol.py      # 协议定义
│   │   ├── remote.py        # 远程执行
│   │   ├── debug.py         # 调试
│   │   └── types.py         # 内部类型
│   ├── managed/         # 托管值（如 RemainingSteps）
│   ├── _internal/       # 内部工具
│   ├── constants.py     # 常量（START, END）
│   ├── errors.py        # 错误类型
│   ├── types.py         # 公共类型（Command, Send, RetryPolicy 等）
│   ├── config.py        # 配置
│   ├── runtime.py       # Runtime 运行时
│   ├── callbacks.py     # 回调
│   ├── typing.py        # 类型变量
│   └── warnings.py      # 弃用警告
├── checkpoint/          # 检查点抽象和序列化
│   ├── base/            # BaseCheckpointSaver, Checkpoint, PendingWrite
│   └── serde/           # 序列化（JSON+, MsgPack, 加密）
├── checkpoint-postgres/ # PostgreSQL 检查点存储
├── checkpoint-sqlite/   # SQLite 检查点存储
├── prebuilt/            # 预构建组件（ToolNode, chat_agent_executor）
├── cli/                # LangGraph CLI
├── sdk-py/             # Python SDK
└── sdk-js/             # JavaScript SDK
```

### 2.2 核心模块关系

```
用户 API 层:  StateGraph / @entrypoint / prebuilt
           ↓ compile()
执行引擎层:  Pregel (main.py)
           ↓
核心算法层:  _algo.py (prepare_next_tasks, apply_writes)
           ↓
执行循环层:  _loop.py (PregelLoop.tick)
           ↓
基础设施层:  channels/ (状态通道) + checkpoint/ (持久化) + _retry.py
```

### 2.3 设计模式

1. **Builder 模式**: `StateGraph` 是构建器，`compile()` 产出 `CompiledStateGraph`
2. **Actor + Channel 模式**: 节点（Actor）通过通道（Channel）通信，实现解耦
3. **BSP (Bulk Synchronous Parallel)**: Plan → Execute → Update 的超步循环
4. **Strategy 模式**: 通道类型通过 `update()` 方法定义不同的聚合策略
5. **Protocol 模式**: `WritesProtocol`、`StreamProtocol` 等接口定义

---

## 3. 核心源码解读

### 3.1 图引擎（Pregel）

`Pregel` 类（`pregel/main.py`，3773 行）是整个框架的心脏。它的设计哲学直接来源于 Google Pregel 论文和 BSP 计算模型。

**三个阶段的超步循环**（来自源码 docstring）：

```python
# Pregel 类文档：
# Each step consists of three phases:
# - Plan: 确定本步执行哪些 actor
# - Execution: 并行执行所有选中的 actor
# - Update: 用 actor 写入的值更新 channels
# 重复直到没有 actor 被选中，或达到最大步数
```

`CompiledStateGraph` 直接继承 `Pregel`：

```python
# langgraph/graph/state.py
class CompiledStateGraph(
    Pregel[StateT, ContextT, InputT, OutputT],
    Generic[StateT, ContextT, InputT, OutputT],
):
    builder: StateGraph[StateT, ContextT, InputT, OutputT]
```

### 3.2 状态管理（State Management）

#### StateGraph 构建

`StateGraph` 使用 TypedDict + Annotated 定义状态 Schema：

```python
# langgraph/graph/state.py
class StateGraph(Generic[StateT, ContextT, InputT, OutputT]):
    """A graph whose nodes communicate by reading and writing to a shared state.
    
    Each state key can optionally be annotated with a reducer function that
    will be used to aggregate the values of that key received from multiple nodes.
    The signature of a reducer function is `(Value, Value) -> Value`.
    """
```

**Schema 到 Channel 的映射**（`_add_schema` 方法）：

```python
def _add_schema(self, schema: type[Any], /, allow_managed: bool = True) -> None:
    channels, managed, type_hints = _get_channels(schema)
    for key, channel in channels.items():
        self.channels[key] = channel
    for key, managed in managed.items():
        self.managed[key] = managed
```

#### 通道系统（Channels）

`BaseChannel` 抽象基类定义了通道的核心接口：

```python
# langgraph/channels/base.py
class BaseChannel(Generic[Value, Update, Checkpoint], ABC):
    @abstractmethod
    def get(self) -> Value: ...           # 读取当前值
    
    @abstractmethod
    def update(self, values: Sequence[Update]) -> bool:  # 应用更新
    
    @abstractmethod
    def from_checkpoint(self, checkpoint: Checkpoint) -> Self:  # 从检查点恢复
    
    def consume(self) -> bool: ...        # 通知已消费（防重复触发）
    def finish(self) -> bool: ...         # 通知图即将结束
```

**关键通道类型**：

| 通道 | 用途 | 更新策略 |
|------|------|---------|
| `LastValue` | 默认，存储最新值 | 每步只能接收一个值 |
| `Topic` | PubSub，多值 | 可累积多值，支持去重 |
| `BinaryOperatorAggregate` | 聚合（如求和） | 用二元运算符合并 |
| `EphemeralValue` | 输入专用 | 不持久化 |
| `LastValueAfterFinish` | 延迟输出 | finish() 后才可用 |
| `UntrackedValue` | 不追踪变化 | 不触发下游节点 |

**LastValue 的实现**：

```python
# langgraph/channels/last_value.py
class LastValue(Generic[Value], BaseChannel[Value, Value, Value]):
    __slots__ = ("value",)

    def update(self, values: Sequence[Value]) -> bool:
        if len(values) == 0:
            return False
        if len(values) != 1:
            raise InvalidUpdateError(
                f"At key '{self.key}': Can receive only one value per step. "
                "Use an Annotated key to handle multiple values."
            )
        self.value = values[-1]
        return True
```

### 3.3 节点和边的定义与执行

#### 节点添加

```python
# StateGraph.add_node 支持多种形式：
# 1. 直接函数
builder.add_node("my_node", my_function)
# 2. Runnable
builder.add_node("my_node", my_runnable)
# 3. 装饰器
@builder.add_node
def my_node(state): ...
```

#### 条件边（Branch）

`BranchSpec` 处理条件路由，在 `_get_channels` 中通过 `Annotated` 的 reducer 自动推断通道类型。

#### 节点执行（PregelNode）

```python
# langgraph/pregel/_read.py
class PregelNode:
    # 将节点包装为 ChannelRead + ChannelWrite 组合
    # ChannelRead: 从指定 channels 读取数据，组装为节点输入
    # ChannelWrite: 将节点输出写入指定 channels
```

### 3.4 持久化和检查点机制

#### Checkpoint 数据结构

```python
# langgraph/checkpoint/base/__init__.py
class Checkpoint(TypedDict):
    v: int                                    # 格式版本
    id: str                                   # 唯一且单调递增的 ID
    ts: str                                   # ISO 8601 时间戳
    channel_values: dict[str, Any]            # 各通道的值快照
    channel_versions: ChannelVersions         # 各通道的版本号
    versions_seen: dict[str, ChannelVersions] # 每个节点看到的版本
    updated_channels: list[str] | None        # 本步更新的通道
```

#### BaseCheckpointSaver

```python
class BaseCheckpointSaver(Generic[V]):
    """Checkpointers allow LangGraph agents to persist their state
    within and across multiple interactions."""
    
    serde: SerializerProtocol = JsonPlusSerializer()
    
    # 核心方法（同步+异步）:
    # - put(config, checkpoint, metadata, pending_writes)
    # - get_tuple(config) -> CheckpointTuple
    # - list(config, filter) -> Iterator[CheckpointTuple]
    # - aput / aget_tuple / alist（异步版本）
```

#### 检查点在执行循环中的使用

在 `_loop.py` 的 `PregelLoop` 中，每步执行后保存检查点：

```python
# langgraph/pregel/_loop.py - PregelLoop.put_writes
def put_writes(self, task_id: str, writes: WritesT) -> None:
    # 保存写入到待处理列表
    self.checkpoint_pending_writes.extend((task_id, c, v) for c, v in writes)
    # 持久化到 checkpointer
    if self.durability != "exit" and self.checkpointer_put_writes is not None:
        self.submit(self.checkpointer_put_writes, config, writes_to_save, task_id)
```

#### Durability 模式

```python
# durability 参数控制持久化时机:
# - "sync": 同步持久化，下一步开始前完成
# - "async": 异步持久化，与下一步并行（默认）
# - "exit": 仅在图退出时持久化
```

#### 序列化

支持三种序列化后端：
- **JsonPlusSerializer**: 默认，JSON + 自定义类型扩展
- **MsgPackSerializer**: 高性能二进制格式（`_serde.STRICT_MSGPACK_ENABLED`）
- **EncryptedSerializer**: 加密序列化

### 3.5 人机交互（Human-in-the-loop）

LangGraph 通过**中断机制**实现人机交互，这是其最核心的设计之一。

#### 中断检测

```python
# langgraph/pregel/_algo.py
def should_interrupt(
    checkpoint: Checkpoint,
    interrupt_nodes: All | Sequence[str],
    tasks: Iterable[PregelExecutableTask],
) -> list[PregelExecutableTask]:
    """Check if the graph should be interrupted based on current state."""
    # 如果有通道自上次中断后有更新，且触发节点在中断列表中
    any_updates_since_prev_interrupt = any(
        version > seen.get(chan, null_version)
        for chan, version in checkpoint["channel_versions"].items()
    )
    return (
        [task for task in tasks
         if (interrupt_nodes == "*" or task.name in interrupt_nodes)]
        if any_updates_since_prev_interrupt
        else []
    )
```

#### 使用方式

```python
# 编译时指定中断点
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["human_review"],  # 在节点前中断
    interrupt_after=["tool_call"],      # 在节点后中断
)

# 节点内动态中断
from langgraph.types import interrupt
def my_node(state):
    user_input = interrupt("请确认是否继续")  # 暂停执行，等待外部输入
    return {"result": user_input}
```

#### 恢复机制

恢复通过 `Command` 对象实现，允许在恢复时注入新的状态更新：

```python
# 恢复执行
from langgraph.types import Command
graph.invoke(Command(resume=user_response), config)
```

### 3.6 流式处理

Pregel 支持多种流式模式，通过 `stream_mode` 参数控制：

| 模式 | 说明 |
|------|------|
| `values` | 每步后输出完整状态 |
| `updates` | 每步后输出状态变更 |
| `messages` | 实时输出 LLM 消息 token |
| `events` | 自定义事件 |
| `custom` | 用户自定义流 |
| `debug` | 调试信息 |

流式实现通过 `StreamProtocol` 接口和 `_messages.py` 中的 `StreamMessagesHandler` 实现。v2 格式返回 `StreamPart` 类型字典，提供更好的类型安全。

---

## 4. 关键算法和机制

### 4.1 Pregel 计算模型的实现

LangGraph 的核心执行模型是 **Pregel + BSP**：

1. **超步循环**（`PregelLoop.tick`）:

```python
# langgraph/pregel/_loop.py
def tick(self) -> bool:
    """Execute a single iteration of the Pregel loop."""
    if self.step > self.stop:
        self.status = "out_of_steps"
        return False
    
    # Phase 1: Plan - 准备下一步要执行的任务
    self.tasks = prepare_next_tasks(
        self.checkpoint, self.checkpoint_pending_writes,
        self.nodes, self.channels, self.managed, ...
    )
    
    # Phase 2: Execute - 执行所有任务
    # ...（异步提交到线程池/事件循环）
    
    # Phase 3: Update - 应用写入
    updated_channels = apply_writes(
        self.checkpoint, self.channels, ...
    )
    
    self.step += 1
    return bool(self.tasks)  # 还有任务则继续
```

2. **任务准备**（`prepare_next_tasks`）:

```python
# langgraph/pregel/_algo.py
def prepare_next_tasks(...) -> dict[str, PregelTask]:
    # 优化：使用 trigger_to_nodes 映射快速确定哪些节点需要执行
    if updated_channels and trigger_to_nodes:
        triggered_nodes = set()
        for channel in updated_channels:
            if node_ids := trigger_to_nodes.get(channel):
                triggered_nodes.update(node_ids)
        candidate_nodes = sorted(triggered_nodes)
    
    # 为每个候选节点准备任务
    for name in candidate_nodes:
        if task := prepare_single_task(...):
            tasks.append(task)
    
    return {t.id: t for t in tasks}
```

3. **写入应用**（`apply_writes`）:

```python
# langgraph/pregel/_algo.py
def apply_writes(checkpoint, channels, tasks, ...) -> set[str]:
    # 按路径排序确保确定性
    tasks = sorted(tasks, key=lambda t: task_path_str(t.path[:3]))
    
    # 按通道分组写入
    for chan, vals in pending_writes_by_channel.items():
        if channels[chan].update(vals):
            checkpoint["channel_versions"][chan] = next_version
            if channels[chan].is_available():
                updated_channels.add(chan)
    
    # 通知未更新的通道
    if bump_step:
        for chan in channels:
            if channels[chan].update(EMPTY_SEQ):
                updated_channels.add(chan)
    
    # 如果是最后一步，通知所有通道 finish
    if bump_step and updated_channels.isdisjoint(trigger_to_nodes):
        for chan in channels:
            if channels[chan].finish():
                updated_channels.add(chan)
    
    return updated_channels
```

### 4.2 消息传递机制

节点间通过**通道**进行消息传递：
- 每个节点声明订阅哪些通道（`PregelNode` 的 `channels` 字段）
- 节点执行时从订阅的通道读取数据
- 节点输出通过 `ChannelWrite` 写入目标通道
- **同一超步内的写入在下个超步才可见**（BSP 语义）

**特殊通道**：
- `INPUT`: 输入通道，每个图有一个
- `TASKS`: Topic 类型通道，用于 `Send` 动态派发任务
- `INTERRUPT`: 中断控制
- `RETURN`: 返回值
- `ERROR`: 错误传播

### 4.3 中断和恢复机制

中断基于**通道版本号**实现：

1. 每次写入会递增通道版本号（`increment` 函数）
2. `should_interrupt` 比较当前版本与上次中断时的版本
3. 如果有更新且目标节点在中断列表中，触发中断
4. 中断后保存检查点，外部可通过 `Command(resume=...)` 恢复

### 4.4 子图（Subgraphs）

子图通过嵌套 `StateGraph` 实现：

- 子图编译后成为父图中的一个节点
- 每个子图有独立的检查点命名空间（`checkpoint_ns`）
- 命名空间使用 `|` 分隔，如 `parent:task_id|child:task_id`
- 父图的 checkpointer 会被子图继承
- `Command` 可以跨子图传播（`Command.PARENT` 冒泡到父图）

---

## 5. API 设计分析

### 5.1 公共 API 的设计哲学

LangGraph 提供三层 API：

1. **Graph API**（`StateGraph`）— 最常用，声明式图构建
2. **Functional API**（`@task` + `@entrypoint`）— 函数式，更 Pythonic
3. **Pregel API**（底层）— 高级用户直接使用

### 5.2 装饰器和类型系统

```python
# 函数式 API
from langgraph.func import task, entrypoint

@task
def my_task(input: str) -> str:
    return process(input)

@entrypoint()
def my_workflow(input: str) -> str:
    result = my_task(input).result()
    return result
```

**类型系统特点**：
- 使用 `typing.Annotated` 将 reducer 附加到类型上
- 使用 `TypedDict` 定义状态 Schema
- `Generic` 参数化 `StateGraph[StateT, ContextT, InputT, OutputT]`
- `ContextT` 提供运行时上下文（如 user_id、db_conn）

### 5.3 与 LangChain 的集成

- `Pregel` 实现了 LangChain 的 `Runnable` 接口（通过内部 `RunnableLike` 适配）
- 节点可以是任何 `Runnable`（LLM Chain、Tool 等）
- 使用 `langchain-core` 的回调系统（`CallbackManager`）
- 消息使用 `langchain_core.messages` 中的类型
- 工具使用 `langchain_core.tools` 中的 `BaseTool`

---

## 6. 部署和生产就绪

### 6.1 LangGraph Platform

- **LangGraph CLI** (`libs/cli/`): 本地开发和部署工具
- **LangGraph SDK** (`libs/sdk-py/`, `libs/sdk-js/`): 与 Platform 通信
- **Remote Pregel** (`pregel/remote.py`): 远程执行支持
- 部署为独立的 API 服务，支持多租户、认证等

### 6.2 扩展性和性能

- **Durability 模式**: `sync`/`async`/`exit` 三级持久化策略
- **缓存**: `BaseCache` + `CachePolicy` 节点级缓存
- **并行执行**: 同步用线程池，异步用 asyncio
- **trigger_to_nodes 优化**: 避免每步遍历所有节点
- **xxhash**: 高性能任务 ID 计算
- **MsgPack 序列化**: 比 JSON 更快的二进制格式

### 6.3 错误处理和重试

```python
# langgraph/types.py - RetryPolicy
@dataclass
class RetryPolicy:
    initial_interval: float = 0.5
    backoff_factor: float = 2.0
    max_interval: float = 128.0
    max_attempts: int = 3
    jitter: bool = True
    retry_on: ...  # 异常类型列表或判断函数
```

重试实现（`_retry.py`）支持：
- 指数退避 + 最大间隔限制
- 可选抖动（jitter）
- 可配置重试异常类型
- 同步和异步版本
- 重试时清除前次写入，保持幂等性

---

## 7. 与竞品对比

| 维度 | LangGraph | CrewAI | AutoGen | Temporal |
|------|-----------|--------|---------|----------|
| **定位** | 通用 Agent 编排 | 多 Agent 协作 | 多 Agent 对话 | 工作流编排 |
| **状态管理** | ✅ 原生有状态 | ⚠️ 有限 | ⚠️ 有限 | ✅ 强大 |
| **Human-in-the-loop** | ✅ 原生中断/恢复 | ❌ 不支持 | ⚠️ 有限 | ✅ 支持 |
| **持久化** | ✅ 多后端 | ❌ 不支持 | ❌ 不支持 | ✅ 强大 |
| **流式处理** | ✅ 多模式 | ❌ 不支持 | ⚠️ 有限 | ❌ 不适用 |
| **LLM 集成** | ✅ LangChain 生态 | ✅ 内置 | ✅ 内置 | ❌ 无 |
| **非 LLM 场景** | ⚠️ 可以但不典型 | ❌ 不适合 | ❌ 不适合 | ✅ 非常适合 |
| **子图/子流程** | ✅ 子图 | ❌ | ⚠️ 有限 | ✅ 子工作流 |
| **部署方案** | ✅ Platform | ⚠️ 有限 | ❌ | ✅ Cloud |
| **学习曲线** | 中等 | 低 | 低 | 高 |

### 优势
- **LLM Agent 领域最成熟的状态管理方案**
- Human-in-the-loop 是一等公民
- 丰富的检查点和时间旅行能力
- 与 LangChain 生态深度集成
- 灵活的 API 层次（声明式/函数式/底层）

### 劣势
- 代码量大（仅核心库 ~9000 行），复杂度高
- 强依赖 LangChain 生态
- 非 LLM 场景不如 Temporal 成熟
- 部署依赖 LangGraph Platform（商业产品）

---

## 8. 适用场景和最佳实践

### 8.1 典型使用场景

1. **多步对话 Agent**: 利用 `add_messages` + 检查点实现对话记忆
2. **RAG 流水线**: 检索 → 重排 → 生成 → 引用的有状态流水线
3. **工具调用 Agent**: 循环调用工具直到完成任务
4. **多 Agent 协作**: Supervisor 或 Swarm 模式的多智能体系统
5. **审批流程**: Human-in-the-loop 的内容审核/决策流程
6. **代码助手**: 计划 → 编码 → 测试 → 修复的迭代循环

### 8.2 设计建议

1. **状态设计**: 使用 TypedDict + Annotated reducer，避免状态爆炸
2. **节点粒度**: 每个节点做一件事，便于测试和复用
3. **检查点选择**: 开发用 `MemorySaver`，生产用 Postgres
4. **中断策略**: 优先使用节点内 `interrupt()` 而非 `interrupt_before/after`
5. **错误处理**: 为可能失败的外部调用配置 `RetryPolicy`
6. **流式输出**: 对 LLM 调用使用 `stream_mode="messages"` 提升体验

---

## 9. 总结和学习建议

### 核心洞察

LangGraph 的本质是将 Google Pregel 的**分布式图计算模型**应用到 LLM Agent 编排领域。其核心创新在于：

1. **通道系统**将状态管理抽象为可组合的单元
2. **检查点机制**使有状态执行变得可中断、可恢复、可调试
3. **BSP 语义**保证了确定性执行顺序
4. **版本号追踪**实现了高效的增量触发

### 学习路径

1. **入门**: 从 `StateGraph` + `add_messages` 构建简单对话 Agent
2. **进阶**: 学习条件边、子图、`Send` 动态派发
3. **深入**: 阅读 `_algo.py` 理解 Pregel 超步循环
4. **精通**: 实现 `BaseCheckpointSaver` 自定义持久化后端
5. **生产**: 学习 LangGraph Platform 部署和监控

### 关键源文件阅读顺序

1. `channels/base.py` → 理解通道抽象
2. `channels/last_value.py` → 理解基本通道实现
3. `graph/state.py` → 理解图构建和编译
4. `pregel/_algo.py` → 理解核心算法（`apply_writes`, `prepare_next_tasks`）
5. `pregel/_loop.py` → 理解执行循环
6. `pregel/_retry.py` → 理解重试机制
7. `pregel/main.py` → 理解完整 Pregel 实现
8. `checkpoint/base/__init__.py` → 理解检查点系统

---

*本报告基于 LangGraph v1.1.9 源码分析生成。*