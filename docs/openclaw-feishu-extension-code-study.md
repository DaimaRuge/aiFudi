# 《OpenClaw Feishu Channel 源码导读：从注册、接入到消息收发全流程》

## 1. 总览

Feishu 插件在 OpenClaw 里，本质上是“把飞书接进 OpenClaw 的一层翻译器 + 连接器”。它不是业务功能本身，而是负责把飞书世界里的概念，比如机器人、群聊、私聊、话题线程、消息卡片、媒体文件、用户 ID，翻译成 OpenClaw 能理解的统一 channel 语言；再把 OpenClaw 产生的回复，翻译回飞书 API 调用。证据在 `index.ts` 的 `defineChannelPluginEntry(...)` 与 `src/channel.ts` 的 `feishuPlugin`。

它和普通业务代码的区别在于：普通业务代码更关心“回答什么”，而这个插件更关心“从哪来、怎么进、怎么发回去”。所以它属于 channel/plugin 层，而不是 agent 或业务层。插件清单 `openclaw.plugin.json` 明确声明了这个插件的 `id` 是 `feishu`，并且它拥有一个 channel：`"channels": ["feishu"]`。也就是说，它是系统里的“飞书入口适配层”。

---

## 2. 先业务、后技术：PM 应该怎么理解它

### 2.1 如果我是 PM，我应该把这个插件理解成什么

把它理解成：

- 一个“飞书接入模块”
- 一个“飞书消息收发网关”
- 一个“飞书能力适配器”

它解决的问题不是“AI 怎么回答”，而是：

- 飞书消息怎么进来
- 哪个用户/群/话题该进哪个 OpenClaw 会话
- 这条消息能不能触发机器人
- 回复应该回到群里、私聊里，还是话题线程里
- 回复是文本、卡片、图片、文件还是 reaction

### 2.2 它解决了哪些飞书接入问题

从代码看，这个插件至少解决了 8 类问题：

1. 插件注册和 channel 声明  
   证据：`openclaw.plugin.json`，`index.ts` 的 `defineChannelPluginEntry(...)`

2. 配置接入  
   证据：`src/config-schema.ts` 的 `FeishuConfigSchema`，`src/channel.ts` 的 `configSchema`

3. 多账号解析  
   证据：`src/accounts.ts` 的 `resolveFeishuAccount(...)`

4. 入站连接方式  
   支持 `websocket` 和 `webhook`  
   证据：`src/config-schema.ts` 的 `FeishuConnectionModeSchema`，`src/monitor.account.ts` 的 `connectionMode`

5. 入站消息解析和路由  
   证据：`src/bot.ts` 的 `parseFeishuMessageEvent(...)`、`handleFeishuMessage(...)`

6. 权限和策略控制  
   私聊策略、群策略、allowlist、是否必须 @  
   证据：`src/policy.ts`，`src/bot.ts`

7. 出站发送  
   文本、卡片、编辑、media、thread-reply  
   证据：`src/send.ts`，`src/media.ts`

8. 扩展动作能力  
   channel-info、member-info、reactions、pins  
   证据：`src/channel.ts` 的 `handleAction(...)`

### 2.3 典型用户路径

一个典型路径是：

1. 用户在飞书群里发消息并 @ 机器人
2. Feishu 插件通过 webhook 或 websocket 收到事件
3. 插件判断这是群聊还是私聊、是否允许触发、应进入哪个 conversation
4. 插件把消息包装成 OpenClaw 的统一入站上下文
5. OpenClaw 运行 agent
6. 插件把 agent 的回复转换成飞书消息/卡片/图片
7. 回复发回原群或原话题

对应证据链：

- 接收：`src/monitor.account.ts` 的 `"im.message.receive_v1"`
- 解析：`src/bot.ts` 的 `parseFeishuMessageEvent(...)`
- 权限判断：`src/bot.ts` 中 group / dm policy 分支
- 构造回复调度器：`src/reply-dispatcher.ts` 的 `createFeishuReplyDispatcher(...)`
- 发回飞书：`src/send.ts` 与 `src/media.ts`

---

## 3. 目录结构拆解

### 3.1 `extensions/feishu` 下的重要文件

#### 最核心文件

- `openclaw.plugin.json`  
  插件清单，声明插件 id、拥有的 channel、skills
- `package.json`  
  声明运行入口 `./index.ts` 和 setup 入口 `./setup-entry.ts`
- `index.ts`  
  插件正式注册入口
- `setup-entry.ts`  
  setup 模式入口
- `src/channel.ts`  
  Feishu channel 的总装配文件，最关键
- `src/runtime.ts`  
  保存插件 runtime 的全局访问点
- `src/config-schema.ts`  
  Feishu 配置 schema
- `src/accounts.ts`  
  多账号配置合并、默认账号、凭据解析
- `src/monitor.ts`  
  启动监控 Feishu provider
- `src/monitor.account.ts`  
  单账号事件监听与事件分发
- `src/monitor.transport.ts`  
  webhook / websocket 传输层
- `src/bot.ts`  
  入站消息主处理器
- `src/bot-content.ts`  
  消息正文、@、topic/session 相关内容解析
- `src/policy.ts`  
  allowlist、群策略、reply policy
- `src/conversation-id.ts`  
  conversation id 编码/解码
- `src/reply-dispatcher.ts`  
  OpenClaw 回复如何落到 Feishu
- `src/send.ts`  
  文本、卡片、编辑、读消息、线程消息 API
- `src/outbound.ts`  
  出站统一适配层
- `src/media.ts`  
  媒体上传、下载、发送
- `src/thread-bindings.ts`  
  线程绑定与 session 绑定
- `src/card-action.ts`  
  卡片点击回调处理
- `src/reactions.ts`  
  reaction API 封装
- `src/chat.ts`  
  chat/member/channel 信息查询
- `src/setup-core.ts`  
  setup 最小接入
- `src/setup-surface.ts`  
  setup wizard 交互式配置
- `api.ts`  
  对外导出 setup / thread / conversation 相关 API
- `setup-api.ts`  
  根目录 re-export 文件，不在 `src/` 下，容易误读

#### 工具与扩展能力文件

- `src/docx.ts`
- `src/wiki.ts`
- `src/drive.ts`
- `src/perm.ts`
- `src/bitable.ts`

### 3.2 按层归类

#### 入口层

- `openclaw.plugin.json`
- `package.json`
- `index.ts`
- `setup-entry.ts`

#### 配置层

- `src/config-schema.ts`
- `src/accounts.ts`
- `src/setup-core.ts`
- `src/setup-surface.ts`
- `src/types.ts`

#### 通信层

- `src/client.ts`
- `src/monitor.ts`
- `src/monitor.account.ts`
- `src/monitor.transport.ts`

#### 消息处理层

- `src/bot.ts`
- `src/bot-content.ts`
- `src/policy.ts`
- `src/conversation-id.ts`
- `src/reply-dispatcher.ts`
- `src/session-route.ts`
- `src/thread-bindings.ts`
- `src/card-action.ts`

#### 工具层

- `src/chat.ts`
- `src/reactions.ts`
- `src/pins.ts`
- `src/card-interaction.ts`
- `src/docx.ts`
- `src/wiki.ts`
- `src/drive.ts`
- `src/perm.ts`
- `src/bitable.ts`

#### 运行时层

- `src/channel.ts`
- `src/channel.runtime.ts`
- `src/runtime.ts`
- `src/outbound.ts`
- `src/send.ts`
- `src/media.ts`

---

## 4. 重点回答：Feishu 如何接入 channel

### 4.1 插件入口在哪里

有两个入口：

1. 正式运行入口：`index.ts`
2. setup 入口：`setup-entry.ts`

`package.json` 也明确声明了：

- `openclaw.extensions = ["./index.ts"]`
- `openclaw.setupEntry = "./setup-entry.ts"`

#### PM 大白话理解

- `index.ts` = “正式上班入口”
- `setup-entry.ts` = “安装向导入口”

### 4.2 channel 是如何声明和注册的

#### 第一步：manifest 先声明“我有一个 channel”

`openclaw.plugin.json`：

```json
{
  "id": "feishu",
  "channels": ["feishu"]
}
```

这说明：

- 插件 id 是 `feishu`
- 它对外提供一个叫 `feishu` 的 channel

OpenClaw 核心会读取这个清单，读取逻辑在 `../../src/plugins/manifest.ts` 的 `loadPluginManifest(...)`，manifest 类型里也明确有 `channels?: string[]`。

#### 第二步：运行入口把 channel plugin 真正注册进系统

`index.ts` 用了 `defineChannelPluginEntry(...)`。  
OpenClaw 核心里，`defineChannelPluginEntry(...)` 的逻辑在 `../../src/plugin-sdk/core.ts`，关键动作是：

- `setRuntime?.(api.runtime)`
- `api.registerChannel({ plugin })`

这一步是真正把 `feishuPlugin` 交给插件注册中心。

#### 第三步：注册中心收下这个 channel

OpenClaw 插件注册中心在 `../../src/plugins/registry.ts`。  
`registerChannel(...)` 的实现会把 channel 放入：

- `registry.channelSetups.push(...)`
- `registry.channels.push(...)`

#### 第四步：系统按 id 取出 channel

取 channel 的入口在：

- `../../src/channels/plugins/load.ts`
- `../../src/channels/plugins/registry.ts`

也就是注册完后，系统可以按 `feishu` 拿到这个 channel plugin。

### 4.3 插件 id、channel 名、能力声明在哪里

#### 插件 id

- `openclaw.plugin.json`
- `index.ts` 的 `id: "feishu"`

#### channel 名

- `openclaw.plugin.json` 的 `"channels": ["feishu"]`
- `src/channel.ts` 的 `base.id = "feishu"`

#### 能力声明

在 `src/channel.ts`：

- `chatTypes: ["direct", "channel"]`
- `threads: true`
- `media: true`
- `reactions: true`
- `edit: true`
- `reply: true`

PM 可把它理解成“这个渠道支持什么按钮”。

### 4.4 setup entry 和 runtime entry 分别是什么

#### setup entry

- 文件：`setup-entry.ts`
- 作用：只暴露 `plugin` 给 setup 流程
- 核心函数：`defineSetupPluginEntry(feishuPlugin)`
- 对应 OpenClaw 核心：`../../src/plugin-sdk/core.ts`

#### runtime entry

- 文件：`index.ts`
- 作用：正式运行时注册 channel、设置 runtime、注册工具
- 核心函数：`defineChannelPluginEntry(...)`
- 对应 OpenClaw 核心：`../../src/plugin-sdk/core.ts`

#### PM 大白话理解

- `setup-entry.ts` 是“安装页”
- `index.ts` 是“正式服务页”

### 4.5 config schema 如何接入

#### Feishu 自己定义 schema

在 `src/config-schema.ts` 定义 `FeishuConfigSchema`

#### channel 把 schema 接进系统

在 `src/channel.ts`：

- `configSchema: buildChannelConfigSchema(FeishuConfigSchema)`

这表示：Feishu 配置不是散落各处，而是先有一份明确 schema，再挂到 channel 上。

#### setup wizard 再把 schema 变成“用户可填写的配置流程”

- `src/setup-surface.ts`
- `src/setup-core.ts`

### 4.6 文字版流程图

```text
openclaw.plugin.json
  -> 声明插件 id=feishu, channels=["feishu"]

package.json
  -> 声明运行入口 index.ts
  -> 声明 setup 入口 setup-entry.ts

index.ts
  -> defineChannelPluginEntry(...)
  -> api.registerChannel({ plugin: feishuPlugin })

src/plugin-sdk/core.ts
  -> defineChannelPluginEntry 内部调用 registerChannel

src/plugins/registry.ts
  -> registry.channelSetups.push(...)
  -> registry.channels.push(...)

src/channel.ts
  -> createChatChannelPlugin(...)
  -> 声明能力、配置、消息动作、网关启动、出站发送

src/channels/plugins/registry.ts
  -> getChannelPlugin("feishu")
  -> 系统正式按 channel 使用它
```

---

## 5. 重点回答：Feishu 如何工作

### 5.1 外部消息进入后的处理链路

真实链路是：

1. `monitorFeishuProvider(...)` 启动 Feishu 监听  
   `src/monitor.ts`

2. `monitorSingleAccount(...)` 根据配置选择 `webhook` 或 `websocket`  
   `src/monitor.account.ts`

3. `registerEventHandlers(...)` 注册飞书事件  
   `src/monitor.account.ts`

4. `im.message.receive_v1` 触发时，进入 `handleFeishuMessage(...)`  
   `src/monitor.account.ts`  
   `src/bot.ts`

5. `handleFeishuMessage(...)` 做解析、权限、路由、构造上下文、调 agent、发回复

### 5.2 conversation id 如何识别和映射

Feishu 没有只用一种会话粒度，它支持：

- 直接私聊
- 群聊
- 群里的 topic
- 群里的 topic + 发送人隔离

所以插件自己设计了一套 conversation id 编码规则，在 `src/conversation-id.ts`：

- `group` -> `chatId`
- `group_sender` -> `chatId:sender:senderOpenId`
- `group_topic` -> `chatId:topic:topicId`
- `group_topic_sender` -> `chatId:topic:topicId:sender:senderOpenId`

解析函数也在同文件。

#### PM 大白话理解

这不是“飞书原生字段”，而是插件为了把不同聊天上下文分清楚，自己发明的一种“会话身份证”。

### 5.3 direct、group、thread/topic 是如何区分的

#### direct / group

在飞书事件里先看 `chat_type`，见 `src/bot.ts` 的 `FeishuMessageEvent` 类型，以及 `handleFeishuMessage(...)`：

- `ctx.chatType === "group"` -> 群聊
- 否则就是 direct

#### topic / thread

`src/bot-content.ts` 的 `resolveFeishuGroupSession(...)` 用：

- `rootId`
- `threadId`
- `groupSessionScope`
- `replyInThread`

来决定是否把这条消息当成 topic 线程消息。

### 5.4 outbound reply / send / edit / card / media 是如何组织的

#### send / card / edit

都在 `src/send.ts`：

- `sendMessageFeishu(...)`
- `sendCardFeishu(...)`
- `editMessageFeishu(...)`
- `getMessageFeishu(...)`
- `listFeishuThreadMessages(...)`

#### media

在 `src/media.ts` 的 `sendMediaFeishu(...)`

#### 统一 outbound 适配

在 `src/outbound.ts` 的 `feishuOutbound`

它做的是：

- 如果文字适合卡片，就走 card
- 如果是本地图片路径，自动转媒体发送
- 如果有文字 + 媒体，先发文字，再发媒体

#### 回复调度

真正从 OpenClaw 回复流转到 Feishu，是 `src/reply-dispatcher.ts` 的 `createFeishuReplyDispatcher(...)`

### 5.5 reactions、member-info、channel-info 这类 action 怎么暴露出去

这些动作统一挂在 channel 的 `actions.handleAction(...)` 里，位置是 `src/channel.ts`

里面明确支持：

- `send`
- `read`
- `edit`
- `thread-reply`
- `pin`
- `list-pins`
- `unpin`
- `member-info`
- `channel-info`
- `channel-list`
- `react`
- `reactions`

也就是说，这些不是“额外散装接口”，而是 Feishu channel 对外暴露的标准动作集。

---

## 6. 消息生命周期分析

下面按 7 步拆解。

### a. 接收

#### 发生什么

Feishu 通过 websocket 或 webhook 把事件送进来。

#### 对应代码

- 总入口：`src/monitor.ts` 的 `monitorFeishuProvider(...)`
- 单账号启动：`src/monitor.account.ts` 的 `monitorSingleAccount(...)`
- websocket：`src/monitor.transport.ts` 的 `monitorWebSocket(...)`
- webhook：`src/monitor.transport.ts` 的 `monitorWebhook(...)`

### b. 解析

#### 发生什么

原始飞书事件被解析成 OpenClaw 更容易处理的 `FeishuMessageContext`。

#### 对应代码

- `src/bot.ts` 的 `parseFeishuMessageEvent(...)`
- `src/bot-content.ts` 的 `parseMessageContent(...)`
- `src/bot-content.ts` 的 `normalizeMentions(...)`

### c. 路由

#### 发生什么

系统要决定：

- 这条消息属于哪个 agent
- 这条消息属于哪个 session key
- 群消息是否按 sender/topic 细分 conversation

#### 对应代码

- group session 解析：`src/bot-content.ts` 的 `resolveFeishuGroupSession(...)`
- conversation id：`src/conversation-id.ts`
- configured binding 路由：`src/bot.ts` 的 `resolveConfiguredBindingRoute(...)`
- route ready：`src/bot.ts` 的 `ensureConfiguredBindingRouteReady(...)`

### d. 权限/策略判断

#### 发生什么

判断这条消息是不是允许机器人处理。

#### 对应代码

- 群策略：`src/bot.ts` 中 group policy 分支
- DM 策略：`src/bot.ts` 中 dm policy 分支
- allowlist：`src/policy.ts`
- reply policy：`src/policy.ts`

### e. 调用 runtime 或 channel plugin

#### 发生什么

消息被转成 OpenClaw 统一上下文，然后交给 channel reply runtime 去执行。

#### 对应代码

- runtime 获取：`src/runtime.ts`
- 上下文收尾：`src/bot.ts` 的 `finalizeInboundContext(...)`
- 创建 reply dispatcher：`src/bot.ts` / `src/reply-dispatcher.ts`
- 调用 OpenClaw 回复调度：`dispatchReplyFromConfig(...)`

### f. 生成回复

#### 发生什么

OpenClaw 生成的回复，会被拆成文本、部分流式内容、卡片、媒体。

#### 对应代码

- 回复调度器：`src/reply-dispatcher.ts`
- 文本/卡片选择：`shouldUseCard(...)`
- streaming card：`FeishuStreamingSession`

### g. 发回飞书

#### 发生什么

最终调用飞书 API 把回复发出去。

#### 对应代码

- 文本：`src/send.ts`
- 卡片：`src/send.ts`
- 编辑：`src/send.ts`
- 媒体：`src/media.ts`

---

## 7. 关键代码实例讲解

### 代码 1：插件正式注册入口

来源：`index.ts`

```ts
export default defineChannelPluginEntry({
  id: "feishu",
  name: "Feishu",
  description: "Feishu/Lark channel plugin",
  plugin: feishuPlugin,
  setRuntime: setFeishuRuntime,
  registerFull(api) {
    registerFeishuSubagentHooks(api);
    registerFeishuDocTools(api);
    registerFeishuChatTools(api);
    registerFeishuWikiTools(api);
    registerFeishuDriveTools(api);
    registerFeishuPermTools(api);
    registerFeishuBitableTools(api);
  },
});
```

#### 白话解释

这段代码在说：

- 我是一个叫 `feishu` 的插件
- 我的核心 channel 定义是 `feishuPlugin`
- 运行时请把 runtime 注入进来
- 正式运行模式下，再额外挂上文档、云盘、权限、知识库等工具

#### 在整体链路里的位置

这是总入口。没有它，Feishu 插件不会被系统正式认识。

#### PM 该关注什么

要看一个插件是不是“只是接消息”，还是“还带业务工具”，这里最清楚。Feishu 不只是聊天接入，还附带 doc/wiki/drive/perm/bitable 工具。

### 代码 2：Feishu channel 的核心声明

来源：`src/channel.ts`

```ts
export const feishuPlugin: ChannelPlugin<ResolvedFeishuAccount, FeishuProbeResult> =
  createChatChannelPlugin({
    base: {
      id: "feishu",
      meta: { ...meta },
      capabilities: {
        chatTypes: ["direct", "channel"],
        polls: false,
        threads: true,
        media: true,
        reactions: true,
        edit: true,
        reply: true,
      },
      configSchema: buildChannelConfigSchema(FeishuConfigSchema),
```

#### 白话解释

这里是在定义“Feishu 这个 channel 到底是什么样”。

- 它叫 `feishu`
- 支持私聊和频道/群
- 支持线程
- 支持媒体
- 支持 reaction
- 支持编辑消息
- 配置结构由 `FeishuConfigSchema` 决定

#### 在整体链路里的位置

这是整个 Feishu channel 的“总说明书”。

#### PM 该关注什么

看产品能力边界，先看这里。你能不能做 thread reply、卡片、media、reaction，这里最权威。

### 代码 3：接收消息事件

来源：`src/monitor.account.ts`

```ts
eventDispatcher.register({
  "im.message.receive_v1": async (data) => {
    const event = data as unknown as FeishuMessageEvent;
    const messageId = event.message?.message_id?.trim();
    if (!tryBeginFeishuMessageProcessing(messageId, accountId)) {
      log(`feishu[${accountId}]: dropping duplicate event for message ${messageId}`);
      return;
    }
    const processMessage = async () => {
      await inboundDebouncer.enqueue(event);
    };
```

#### 白话解释

这段代码是在说：

- 监听飞书的“收到消息”事件
- 先拿 message id
- 先做去重，避免同一条消息被处理两次
- 再把消息塞进防抖队列

#### 在整体链路里的位置

这是飞书消息真正进入系统的第一站。

#### PM 该关注什么

这里体现了两个产品稳定性设计：

- 去重：避免重复回复
- 防抖：避免用户连续短句把机器人打爆

### 代码 4：把飞书事件解析成内部上下文

来源：`src/bot.ts`

```ts
export function parseFeishuMessageEvent(
  event: FeishuMessageEvent,
  botOpenId?: string,
  _botName?: string,
): FeishuMessageContext {
  const rawContent = parseMessageContent(event.message.content, event.message.message_type);
  const mentionedBot = checkBotMentioned(event, botOpenId);
  const hasAnyMention = (event.message.mentions?.length ?? 0) > 0;
  const content = normalizeMentions(rawContent, event.message.mentions, botOpenId);
```

#### 白话解释

这段代码做的就是“翻译”：

- 把飞书消息内容拿出来
- 判断有没有 @ 机器人
- 把 mention 标签规范化
- 提取 chatId、messageId、senderId

#### 在整体链路里的位置

这是“飞书原生数据”转“OpenClaw 可处理上下文”的关键一步。

#### PM 该关注什么

你以后讨论“机器人为什么没回”“为什么识别不到 @”“为什么 sender 错了”，核心都要看这里。

### 代码 5：群 session 如何按 topic / sender 切分

来源：`src/bot-content.ts`

```ts
export function resolveFeishuGroupSession(params: {
  chatId: string;
  senderOpenId: string;
  messageId: string;
  rootId?: string;
  threadId?: string;
  groupConfig?: { groupSessionScope?: GroupSessionScope };
  feishuCfg?: { groupSessionScope?: GroupSessionScope };
}): ResolvedFeishuGroupSession {
  const threadReply = Boolean(normalizedThreadId || normalizedRootId);
  const replyInThread =
    (groupConfig?.replyInThread ?? feishuCfg?.replyInThread ?? "disabled") === "enabled" ||
    threadReply;
```

#### 白话解释

这段代码在决定：

- 这条群消息是算整个群一个会话
- 还是“群 + 发言人”一个会话
- 还是“群 + topic”一个会话
- 还是“群 + topic + 发言人”一个会话

#### 在整体链路里的位置

这是 session 路由的核心。

#### PM 该关注什么

如果产品上要讨论“群里每个人是不是要独立上下文”“topic 要不要独立会话”，你讨论的就是这里。

### 代码 6：回复发回飞书

来源：`src/send.ts`

```ts
export async function sendMessageFeishu(
  params: SendFeishuMessageParams,
): Promise<FeishuSendResult> {
  const { cfg, to, text, replyToMessageId, replyInThread, mentions, accountId } = params;
  const { client, receiveId, receiveIdType } = resolveFeishuSendTarget({ cfg, to, accountId });

  let rawText = text ?? "";
  if (mentions && mentions.length > 0) {
    rawText = buildMentionedMessage(mentions, rawText);
  }
```

#### 白话解释

这段代码负责：

- 找到要发给谁
- 如果需要 @ 某些人，先把消息文本改写好
- 再把消息转换成飞书支持的格式
- 最后调用飞书发送 API

#### 在整体链路里的位置

这是最终“把回复发出去”的关键函数之一。

#### PM 该关注什么

“回复展示效果”问题，比如表格、@人、格式转换，核心看这里。

### 代码 7：统一 reply dispatcher

来源：`src/reply-dispatcher.ts`

```ts
export function createFeishuReplyDispatcher(params: CreateFeishuReplyDispatcherParams) {
  const core = getFeishuRuntime();
  const {
    cfg,
    agentId,
    chatId,
    replyToMessageId,
    skipReplyToInMessages,
    replyInThread,
    threadReply,
```

#### 白话解释

这段代码的职责不是“直接发消息”，而是“组织怎么发”。

它负责处理：

- 是否带 typing indicator
- 是否走 streaming card
- 是否走普通文本
- 是否分块发送
- 是否带媒体
- 是否回复到 thread

#### 在整体链路里的位置

这是 OpenClaw 回复流和 Feishu 发信 API 之间的“总调度器”。

#### PM 该关注什么

如果以后要做“流式卡片”“逐步输出”“带 Agent 身份标识的回复头部”，都要看这层。

---

## 8. 架构设计分析

### 8.1 插件化

#### 代码证据

- manifest 声明：`openclaw.plugin.json`
- 运行注册：`index.ts`
- 核心注册入口：`../../src/plugin-sdk/core.ts`
- 注册中心：`../../src/plugins/registry.ts`

#### 这是什么意思

Feishu 不是硬编码在 OpenClaw 主程序里，而是作为独立插件接进去。

#### 对产品扩展的价值

以后再加 Slack、Line、企业微信，模式可以复用，不用改整套系统。

### 8.2 适配器模式

#### 代码证据

- `createChatChannelPlugin(...)`
- `feishuOutbound`
- `createFeishuReplyDispatcher(...)`

#### 这是什么意思

飞书 API 很“飞书味”，OpenClaw 内部上下文很“OpenClaw 味”，中间靠适配器做翻译。

#### 产品价值

换接入渠道时，产品层的 agent、session、reply 逻辑可以尽量不变。

### 8.3 配置驱动

#### 代码证据

- schema：`src/config-schema.ts`
- channel 挂载 configSchema：`src/channel.ts`
- setup wizard：`src/setup-surface.ts`

#### 这是什么意思

很多行为不是写死的，而是配出来的：

- websocket / webhook
- dmPolicy
- groupPolicy
- groupSessionScope
- replyInThread
- actions.reactions
- typingIndicator

#### 产品价值

以后你要做“同一个功能对不同客户配置不同规则”，更容易。

### 8.4 运行时解耦

#### 代码证据

- runtime store：`src/runtime.ts`
- 正式注册时注入 runtime：`index.ts`
- lazy runtime：`src/channel.ts`

#### 这是什么意思

channel 定义和具体 runtime 能力是分开的。

#### 产品价值

setup 阶段、正式运行阶段、测试阶段可以用不同程度的能力，不会硬绑死。

### 8.5 账号隔离

#### 代码证据

- 多账号 schema：`src/config-schema.ts`
- 账号解析：`src/accounts.ts`
- 列出启用账号：`src/accounts.ts`
- 单账号 monitor：`src/monitor.account.ts`

#### 这是什么意思

Feishu 插件不是只支持一个 bot，可按 account 配多个。

#### 产品价值

一个 OpenClaw 可以同时接多个飞书应用、多个租户或多个环境。

### 8.6 能力声明

#### 代码证据

- `capabilities`：`src/channel.ts`
- message tool actions：`src/channel.ts`

#### 这是什么意思

系统不会猜这个渠道能做什么，而是插件自己声明。

#### 产品价值

产品做能力矩阵、渠道对比、灰度支持时，有统一依据。

### 8.7 会话隔离与线程绑定

#### 代码证据

- `src/conversation-id.ts`
- `src/bot-content.ts` 的 `resolveFeishuGroupSession(...)`
- `src/thread-bindings.ts` 的 `createFeishuThreadBindingManager(...)`

#### 这是什么意思

Feishu 群、topic、topic+sender 可以映射成不同 session。

#### 产品价值

能支持更精细的上下文隔离，避免“一个群里所有人共用同一个脑子”。

---

## 9. 我作为 PM 该怎么读懂它

### 9.1 第一轮先读哪些

按顺序读：

1. `openclaw.plugin.json`
2. `package.json`
3. `index.ts`
4. `src/channel.ts`
5. `src/config-schema.ts`

### 9.2 第二轮读哪些

1. `src/monitor.ts`
2. `src/monitor.account.ts`
3. `src/bot.ts`
4. `src/reply-dispatcher.ts`
5. `src/send.ts`
6. `src/media.ts`

### 9.3 哪些文件可以先跳过

先跳过这些“扩展能力文件”：

- `src/docx.ts`
- `src/wiki.ts`
- `src/drive.ts`
- `src/perm.ts`
- `src/bitable.ts`
- 各种 `*.test.ts`

### 9.4 30 分钟学习路径

1. 读 `openclaw.plugin.json`
2. 读 `package.json`
3. 读 `index.ts`
4. 读 `src/channel.ts`
5. 只看 `src/channel.ts` 里的这些块：
   - `capabilities`
   - `configSchema`
   - `actions`
   - `gateway.startAccount`
   - `outbound`

### 9.5 2 小时学习路径

在 30 分钟路径基础上，再读：

1. `src/config-schema.ts`
2. `src/accounts.ts`
3. `src/monitor.account.ts`
4. `src/bot.ts`
5. `src/reply-dispatcher.ts`
6. `src/send.ts`

### 9.6 半天学习路径

在 2 小时路径基础上，再读：

1. `src/bot-content.ts`
2. `src/policy.ts`
3. `src/conversation-id.ts`
4. `src/thread-bindings.ts`
5. `src/media.ts`
6. `../../src/plugin-sdk/core.ts`
7. `../../src/plugins/registry.ts`
8. `../../src/plugins/manifest.ts`

---

## 10. 总结卡片

### 10.1 Feishu 接入 channel 的一句话总结

Feishu 插件通过 `openclaw.plugin.json` 声明自己拥有 `feishu` channel，再在 `index.ts` 用 `defineChannelPluginEntry(...)` 把 `feishuPlugin` 注册进 OpenClaw 的 channel 注册中心。

### 10.2 消息工作流一句话总结

飞书消息经 `monitor -> monitor.account -> bot -> reply-dispatcher -> send/media` 这条链路进入系统、完成权限和会话路由、再以文本/卡片/媒体形式发回飞书。

### 10.3 最关键的 10 个文件/函数

1. `index.ts` `defineChannelPluginEntry(...)`
2. `src/channel.ts` `feishuPlugin`
3. `src/config-schema.ts` `FeishuConfigSchema`
4. `src/accounts.ts` `resolveFeishuAccount(...)`
5. `src/monitor.ts` `monitorFeishuProvider(...)`
6. `src/monitor.account.ts` `monitorSingleAccount(...)`
7. `src/bot.ts` `handleFeishuMessage(...)`
8. `src/bot-content.ts` `resolveFeishuGroupSession(...)`
9. `src/reply-dispatcher.ts` `createFeishuReplyDispatcher(...)`
10. `src/send.ts` `sendMessageFeishu(...)`

### 10.4 最容易看不懂的 5 个点

1. `conversationId` 不是飞书原生字段，而是插件自己设计的会话编码  
   证据：`src/conversation-id.ts`

2. `threadId` 和 `rootId` 含义不同  
   代码里多次优先用 `rootId` 作为真正回复锚点，见 `src/bot.ts`

3. `setup-entry.ts` 和 `index.ts` 是两个不同入口  
   一个用于配置，一个用于正式运行

4. `src/channel.ts` 不是“发消息代码”，而是“整个 channel 的总装配表”

5. `src/reply-dispatcher.ts` 不是业务回复生成器，而是“把生成好的回复组织成飞书发信动作”

### 10.5 建议下一步继续看的模块

1. `src/bot.ts`
2. `src/reply-dispatcher.ts`
3. `src/bot-content.ts`
4. `../../src/plugin-sdk/core.ts`
5. `../../src/plugins/registry.ts`

---

## 11. 深入补充：OpenClaw 外层到底怎么发现并加载 Feishu 插件

这一节回答一个更外层的问题：Feishu 不是凭空出现的，OpenClaw 外层是怎么从磁盘把它找出来的？

### 11.1 从哪里发现插件

最外层发现逻辑在 `../../src/plugins/discovery.ts` 的 `discoverOpenClawPlugins(...)`。

它会按来源找插件：

- `config`：显式配置路径
- `workspace`：工作区插件目录
- `bundled`：仓库自带的 `extensions/`
- `global`：全局安装目录

从代码看，当前仓库内的 Feishu 属于 `bundled` 来源。`discoverOpenClawPlugins(...)` 会扫描插件目录、读 `package.json` 的 `openclaw.extensions` 和 `openclaw.setupEntry`，然后生成 `PluginCandidate`。

#### PM 大白话理解

OpenClaw 不是“写死去 import Feishu”，而是先做一轮“插件搜寻”。

### 11.2 Feishu 为什么会被识别成 bundled plugin

`package.json` 里有：

- `openclaw.extensions: ["./index.ts"]`
- `openclaw.setupEntry: "./setup-entry.ts"`

而 `openclaw.plugin.json` 里有：

- `id: "feishu"`
- `channels: ["feishu"]`

于是 OpenClaw 会把它识别成：

- 一个可运行插件
- 有一个 setup 入口
- 提供一个 channel

### 11.3 manifest registry 在做什么

`../../src/plugins/manifest-registry.ts` 的 `loadPluginManifestRegistry(...)` 会把 discovery 找到的候选插件，进一步读取 manifest，产出结构化的 `PluginManifestRecord`。

这里会保留的信息包括：

- `id`
- `channels`
- `skills`
- `rootDir`
- `source`
- `setupSource`

这也是后面系统能知道“Feishu 有 setup 入口、也有 runtime 入口”的原因。

### 11.4 active plugin registry 在做什么

`../../src/plugins/runtime.ts` 用 `setActivePluginRegistry(...)` / `requireActivePluginRegistry(...)` 管理“当前已激活插件注册表”。

而 `../../src/channels/plugins/registry.ts` 读的就是这个 active registry。

#### 这对 PM 的意义

这说明“插件发现”和“插件运行”是两阶段：

1. 先扫目录，知道有哪些插件
2. 再激活并注册到运行态

这是一种很标准的插件平台架构。

---

## 12. 深入补充：Setup 流程到底在帮用户配置什么

如果你把 Feishu 插件理解成一个产品接入向导，那 `src/setup-surface.ts` 是最接近产品设计稿的文件。

### 12.1 setup-core 和 setup-surface 的分工

#### `src/setup-core.ts`

职责很少，只做最小必要动作：

- `resolveAccountId`
- `applyAccountConfig(...)`

它更像“配置写入适配器”。

#### `src/setup-surface.ts`

职责更像“交互式安装向导”：

- 是否已配置
- 提示用户去哪里拿 App ID / Secret
- 输入 App Secret
- 选择 websocket / webhook
- webhook 时继续输入 verification token / encrypt key / path
- 选择 domain
- 选择群策略
- 录入 allowlist

### 12.2 setup 流程的产品语言翻译

这套向导实质上在引导用户回答 6 个产品问题：

1. 你的 Feishu 应用凭据是什么？
2. 你走 websocket 还是 webhook？
3. 你的飞书环境是中国版还是国际版？
4. 私聊默认怎么放行？
5. 群聊默认怎么放行？
6. 哪些用户/群有权限触发？

### 12.3 为什么 setup 不是直接编辑配置文件

因为 schema 虽然能约束格式，但不能告诉用户“为什么要填这个”。  
`src/setup-surface.ts` 把“底层字段”翻译成了“交互式问题”。

这对 PM 很重要：  
配置 schema 是“系统视角”，setup wizard 是“用户视角”。

---

## 13. 深入补充：账号、凭据、权限、会话、线程、卡片、媒体分别由哪些文件负责

这是你最关心的一节，我把职责做成一张“责任地图”。

### 13.1 配置

- 总 schema：`src/config-schema.ts`
- setup 写入：`src/setup-core.ts`
- setup 向导：`src/setup-surface.ts`
- 类型定义：`src/types.ts`

### 13.2 账号

- 账号解析：`src/accounts.ts`
- 默认账号选择：`src/accounts.ts` 的 `resolveDefaultFeishuAccountSelection(...)`
- 账号凭据解析：`src/accounts.ts` 的 `resolveFeishuCredentials(...)`
- 已启用账号枚举：`src/accounts.ts` 的 `listEnabledFeishuAccounts(...)`

### 13.3 会话 ID / conversation ID

- 编码 / 解码规则：`src/conversation-id.ts`
- 群 session scope 计算：`src/bot-content.ts` 的 `resolveFeishuGroupSession(...)`
- 出站 session route：`src/session-route.ts`

### 13.4 线程 / topic

- topic 会话计算：`src/bot-content.ts`
- thread 历史拉取：`src/send.ts` 的 `listFeishuThreadMessages(...)`
- thread 绑定注册：`src/thread-bindings.ts`
- subagent 线程继承：`src/subagent-hooks.ts`

### 13.5 权限

- allowlist 匹配：`src/policy.ts` 的 `resolveFeishuAllowlistMatch(...)`
- 群策略判断：`src/policy.ts` 的 `isFeishuGroupAllowed(...)`
- reply policy：`src/policy.ts` 的 `resolveFeishuReplyPolicy(...)`
- setup 时配置 policy：`src/setup-surface.ts`

### 13.6 消息卡片

- 发送卡片：`src/send.ts` 的 `sendCardFeishu(...)`
- 结构化卡片构建：`src/send.ts` 的 `buildStructuredCard(...)`
- 流式卡片：`src/streaming-card.ts`
- 卡片点击入口：`src/card-action.ts`
- 卡片 payload 解码：`src/card-interaction.ts`
- 审批交互卡片：`src/card-ux-approval.ts`

### 13.7 媒体能力

- 上传 / 下载 / 发送总入口：`src/media.ts`
- 入站媒体解析：`src/bot-content.ts` 的 `resolveFeishuMediaList(...)`
- 出站统一适配：`src/outbound.ts`

### 13.8 channel 信息与成员信息

- chat info：`src/chat.ts` 的 `getChatInfo(...)`
- chat members：`src/chat.ts` 的 `getChatMembers(...)`
- member info：`src/chat.ts` 的 `getFeishuMemberInfo(...)`
- 暴露为 action：`src/channel.ts` 的 `handleAction(...)`

---

## 14. 深入补充：卡片点击为什么也能变成“消息”

这是一个很值得 PM 理解的设计。

### 14.1 现象

飞书里点击一张卡片按钮，本来不是普通聊天消息。

### 14.2 代码里怎么做

在 `src/card-action.ts`，它把卡片点击事件重新包装成一个“合成消息”：

- `buildSyntheticMessageEvent(...)`
- `dispatchSyntheticCommand(...)`

最终还是调用：

- `handleFeishuMessage(...)`

### 14.3 这意味着什么

它没有为“卡片点击”再维护一套完全独立的业务链路，而是把它收敛回统一消息入口。

#### PM 大白话理解

卡片点击被系统“伪装成了一条用户消息”。

这有两个好处：

1. 统一权限判断
2. 统一 session 路由

也就是说，卡片交互不是旁路，而是回到主路。

---

## 15. 深入补充：为什么 thread-bindings 是单独一层

`src/thread-bindings.ts` 很容易被忽略，但它其实非常关键。

### 15.1 它解决什么问题

假设：

- 父 agent 在一个 Feishu topic 里工作
- 它启动一个 subagent
- subagent 的回复也应该回到同一个 topic

如果没有 thread binding，子任务就可能“丢线程”，回到普通群聊或错误上下文。

### 15.2 代码怎么做

`createFeishuThreadBindingManager(...)` 会：

- 按 `accountId + conversationId` 建绑定
- 注册到 `registerSessionBindingAdapter(...)`
- 支持 `bindConversation(...)`
- 支持 `resolveByConversation(...)`
- 支持 `touch(...)`
- 支持 `unbind(...)`

### 15.3 对产品的价值

这意味着“会话连续性”不只在主 agent 上成立，在子任务链路上也成立。

如果你要做：

- 子代理协作
- 审批后继续在原线程回复
- topic 内持续跟进

这层都非常重要。

---

## 16. 深入补充：Feishu 插件的“统一翻译思想”

如果你只记住一个架构结论，我建议记住这个：

> Feishu 插件最核心的设计，不是某个 API，而是“把不同来源的飞书事件统一翻译成 OpenClaw 的会话与回复模型”。

它的统一翻译动作主要体现在 4 件事：

1. 入站统一成 `FeishuMessageContext`  
   `src/bot.ts`

2. 会话统一成 `conversationId / sessionKey`  
   `src/conversation-id.ts`、`src/session-route.ts`、`src/bot-content.ts`

3. 回复统一成 `ReplyDispatcher`  
   `src/reply-dispatcher.ts`

4. 出站统一成 `send / card / media / edit`  
   `src/send.ts`、`src/media.ts`、`src/outbound.ts`

从产品视角看，这种设计最大的价值是：

- 新增一个 Feishu 事件类型，不一定要推翻整套系统
- 新增一个新的回复形式，也不一定要改 agent 主逻辑
- 大部分复杂性被收敛在 channel 适配层，不污染业务层

---

## 17. 最终结论

### 17.1 用一句最产品的话总结

Feishu 插件就是 OpenClaw 的“飞书接入中台”：它把飞书的消息、用户、群、topic、卡片、媒体、权限、账号全部翻译成 OpenClaw 的统一会话和回复体系。

### 17.2 用一句最架构的话总结

Feishu 通过 `manifest -> plugin entry -> channel plugin -> monitor -> bot -> reply-dispatcher -> send/media` 这条链，完成了从插件发现、channel 注册、消息入站、会话路由、权限判断到回复出站的完整闭环。

### 17.3 后续最值得继续深挖的 5 个点

1. `src/bot.ts` 中 route / ACP / binding 的完整分支
2. `src/reply-dispatcher.ts` 中 streaming card 的完整策略
3. `src/thread-bindings.ts` 与 `src/subagent-hooks.ts` 的联动
4. `src/channel.ts` 的 action 暴露如何被上层工具调用
5. `../../src/plugins/discovery.ts` 到实际启动命令之间的最外层调用链

---

## 18. 说明：当前还不能完全确定的地方

下面这些点，我明确标注为“当前不能从已读代码完全确定”：

1. OpenClaw 启动命令最外层哪个文件最终调用了 active plugin registry 的完整装载  
   原因：这次已追到 discovery / manifest-registry / registry / runtime state，但还没继续向 CLI / gateway 启动最顶层追完整调用栈

2. Feishu 某些 doc/wiki/drive/perm 工具在真实用户路径里默认是否总会注册  
   原因：这些还受 `tools` 配置项控制，工具注册逻辑已读，但没有再追到全局工具装配与 UI 暴露层

如果下一轮继续，我建议做两篇补充文档：

1. 《OpenClaw Feishu 消息调用链逐函数深挖》
2. 《OpenClaw Feishu 配置项全解与产品行为映射》
