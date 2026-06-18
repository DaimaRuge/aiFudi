# OpenClaw 开源项目深度研究报告 - 第一章

# 项目概述与身份分析

**仓库：** https://github.com/openclaw/openclaw
**研究日期：** 2026-03-24
**报告版本：** v1.0
**研究者：** Claude AI Agent

---

## 1. 项目身份与目的

### 1.1 基本信息

| 指标 | 值 |
|------|-----|
| **项目名称** | OpenClaw |
| **开源协议** | MIT License |
| **主语言** | TypeScript (98%+) / Python (少量脚本) |
| **当前版本** | 2026.3.24 |
| **运行时要求** | Node.js 22.16+ (推荐 Node 24) |
| **包管理器** | pnpm 10.32.1 |
| **主页** | https://openclaw.ai |
| **文档** | https://docs.openclaw.ai |
| **Discord** | https://discord.gg/clawd |

### 1.2 项目定位

**一句话定义：** OpenClaw 是一个**本地优先的个人 AI 助手**，可以在用户自己的设备上运行，通过多种消息渠道（WhatsApp、Telegram、Slack、Discord 等）与用户交互。

**核心价值主张：**
- **本地优先**：数据和控制权完全掌握在用户手中
- **多渠道整合**：支持 20+ 种消息平台，统一入口
- **真正的 AI 代理**：不仅能对话，还能执行实际任务（运行命令、浏览网页、控制设备）
- **可扩展架构**：插件系统支持自定义功能和集成

### 1.3 问题域分析

OpenClaw 解决的核心问题：

1. **AI 助手的隐私问题**：商业 AI 服务通常需要将数据发送到云端，OpenClaw 允许在本地运行
2. **多渠道碎片化**：用户需要在不同的消息应用中使用不同的 AI 工具，OpenClaw 提供统一入口
3. **AI 能力受限**：大多数 AI 只能对话，OpenClaw 的 AI 可以执行实际任务（运行命令、操作文件等）
4. **定制化困难**：商业 AI 服务难以深度定制，OpenClaw 提供完整的插件和技能系统

### 1.4 项目成熟度

**成熟度评估：⭐⭐⭐⭐ (稳定/生产可用)**

依据：
- 活跃的开发团队（20+ 核心维护者）
- 完整的 CI/CD 流程
- 详尽的文档体系
- 多平台支持（macOS、iOS、Android、Linux、Windows WSL2）
- 定期发布周期（日期版本号：vYYYY.M.D）

---

## 2. 技术栈指纹

### 2.1 核心技术栈

```
运行时: Node.js 24 (推荐) / Node.js 22.16+
语言: TypeScript 5.9+
框架: Express 5.x (HTTP) + Hono 4.x (轻量HTTP)
 WebSocket (ws 8.x)
构建: tsdown 0.21.x (基于 esbuild)
测试: Vitest 4.x + Playwright
包管理: pnpm 10.32.1 (monorepo)
部署: Docker + Kubernetes 支持
CI/CD: GitHub Actions
```

### 2.2 核心依赖分析

| 依赖 | 版本 | 用途 | 重要性 |
|------|------|------|--------|
| `@modelcontextprotocol/sdk` | 1.27.1 | MCP 协议支持 | 核心 |
| `@agentclientprotocol/sdk` | 0.16.1 | ACP 代理协议 | 核心 |
| `@mariozechner/pi-*` | 0.61.1 | Pi Agent 运行时 | 核心 |
| `express` | 5.2.1 | HTTP 服务器 | 核心 |
| `ws` | 8.20.0 | WebSocket 通信 | 核心 |
| `playwright-core` | 1.58.2 | 浏览器自动化 | 重要 |
| `sharp` | 0.34.5 | 图像处理 | 重要 |
| `zod` | 4.3.6 | Schema 验证 | 重要 |
| `@sinclair/typebox` | 0.34.48 | 运行时类型 | 重要 |

### 2.3 Monorepo 结构

项目采用 pnpm workspace 管理的 monorepo 结构：

```
openclaw/
├── src/ # 核心源码 (主包)
├── extensions/ # 扩展包 (70+ 扩展)
│ ├── anthropic/ # Anthropic 提供商
│ ├── openai/ # OpenAI 提供商
│ ├── telegram/ # Telegram 渠道
│ ├── discord/ # Discord 渠道
│ ├── slack/ # Slack 渠道
│ └── ... # 更多扩展
├── packages/ # 子包
│ ├── clawdbot/ # ClawDBot 子项目
│ └── moltbot/ # MoltBot 子项目
├── apps/ # 移动应用
│ ├── android/ # Android 原生应用
│ ├── ios/ # iOS 原生应用
│ └── macos/ # macOS 桌面应用
├── ui/ # Web UI (Lit)
├── skills/ # 技能包
└── docs/ # 文档
```

---

## 3. 高层架构概览

### 3.1 架构模式

**主要模式：** 模块化单体 (Modular Monolith) + 插件架构

**证据：**
- `src/plugin-sdk/` - 完整的插件 SDK
- `extensions/` - 70+ 独立扩展包
- `src/plugins/` - 插件加载和管理系统

### 3.2 架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│ External Channels │
│ WhatsApp | Telegram | Slack | Discord | Signal | iMessage | ... │
└────────────────────────────────┬────────────────────────────────────┘
 │
 ▼
┌─────────────────────────────────────────────────────────────────────┐
│ Gateway Server │
│ (WebSocket Control Plane) │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Auth & │ │ Session │ │ Channel │ │
│ │ Security │ │ Management │ │ Routing │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ │
└────────────────────────────────┬────────────────────────────────────┘
 │
 ┌────────────┼────────────┐
 ▼ ▼ ▼
 ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
 │ Pi Agent │ │ Control │ │ Node │
 │ (RPC Mode) │ │ UI │ │ Clients │
 └──────────────┘ └──────────────┘ └──────────────┘
 │ │
 ▼ ▼
 ┌──────────────┐ ┌──────────────┐
 │ Model │ │ Device │
 │ Providers │ │ Actions │
 │ (Anthropic, │ │ (macOS/iOS/ │
 │ OpenAI...) │ │ Android) │
 └──────────────┘ └──────────────┘
```

### 3.3 核心组件

| 组件 | 目录 | 职责 |
|------|------|------|
| **Gateway** | `src/gateway/` | WebSocket 控制平面，会话管理，路由 |
| **Agent Runtime** | `src/agents/` | AI 代理执行，模型调用，工具执行 |
| **ACP** | `src/acp/` | Agent Client Protocol 实现 |
| **Channels** | `src/channels/` + `extensions/` | 消息渠道适配器 |
| **Plugins** | `src/plugins/` | 插件加载，生命周期管理 |
| **CLI** | `src/cli/` | 命令行界面 |
| **Session** | `src/sessions/` | 会话状态管理 |
- **Config** | `src/config/` | 配置加载和验证 |
| **Security** | `src/security/` | 安全策略，权限控制 |
| **Cron** | `src/cron/` | 定时任务调度 |

---

## 4. 仓库结构地图

### 4.1 目录树（注释版）

```
openclaw/
├── src/ # 核心源码
│ ├── entry.ts # CLI 入口点
│ ├── index.ts # 库导出入口
│ ├── gateway/ # Gateway 服务器 (100+ 文件)
│ │ ├── server.impl.ts # 主服务器实现
│ │ ├── boot.ts # 启动引导
│ │ ├── auth.ts # 认证系统
│ │ └── protocol/ # WebSocket 协议
│ ├── agents/ # AI 代理系统
│ │ ├── acp-spawn.ts # ACP 进程管理
│ │ ├── auth-profiles/ # 认证配置
│ │ └── provider-* # 模型提供商
│ ├── acp/ # Agent Client Protocol
│ │ ├── client.ts # ACP 客户端
│ │ ├── server.ts # ACP 服务端
│ │ └── control-plane/ # 控制平面
│ ├── channels/ # 消息渠道核心
│ │ └── plugins/ # 渠道插件接口
│ ├── plugins/ # 插件系统
│ │ ├── loader.ts # 插件加载器
│ │ ├── registry.ts # 插件注册表
│ │ └── install.ts # 插件安装
│ ├── plugin-sdk/ # 插件 SDK (100+ 导出)
│ ├── cli/ # CLI 命令
│ │ ├── program/ # Commander 命令
│ │ └── run-main.js # CLI 主入口
│ ├── config/ # 配置系统
│ ├── sessions/ # 会话管理
│ ├── security/ # 安全系统
│ ├── cron/ # 定时任务
│ ├── browser/ # 浏览器控制
│ ├── canvas-host/ # Canvas 主机
│ ├── node-host/ # 节点主机
│ ├── memory/ # 内存/存储
│ └── utils/ # 工具函数
├── extensions/ # 扩展包 (70+)
│ ├── anthropic/ # Anthropic Claude
│ ├── openai/ # OpenAI GPT
│ ├── google/ # Google Gemini
│ ├── telegram/ # Telegram 渠道
│ ├── discord/ # Discord 渠道
│ ├── slack/ # Slack 渠道
│ ├── whatsapp/ # WhatsApp 渠道
│ ├── signal/ # Signal 渠道
│ ├── matrix/ # Matrix 渠道
│ └── ... # 更多扩展
├── apps/ # 原生应用
│ ├── android/ # Android 应用 (Kotlin)
│ ├── ios/ # iOS 应用 (Swift)
│ ├── macos/ # macOS 应用 (Swift)
│ └── shared/ # 共享代码 (OpenClawKit)
├── ui/ # Web UI
│ └── src/ # Lit 组件
├── skills/ # 技能包
│ ├── model-usage/ # 模型使用追踪
│ └── skill-creator/ # 技能创建工具
├── docs/ # 文档 (Mintlify)
├── test/ # 测试文件
├── scripts/ # 构建脚本
├── vendor/ # 第三方代码
└── .github/workflows/ # CI/CD 配置
```

### 4.2 入口点地图

| 入口类型 | 文件路径 | 说明 |
|---------|---------|------|
| **CLI Binary** | `openclaw.mjs` | npm bin 入口 |
| **CLI Main** | `src/entry.ts:89` | 主入口，启动 CLI |
| **Library** | `src/index.ts` | 库模式导出 |
| **Gateway** | `src/gateway/server.impl.ts` | Gateway 服务器 |
| **Agent RPC** | `src/agents/acp-spawn.ts` | Agent RPC 模式 |

---

## 5. 核心模块与组件

### 5.1 模块职责矩阵

| 模块 | 目录 | 核心职责 | 依赖层级 |
|------|------|---------|---------|
| **Entry** | `src/entry.ts` | 进程启动、CLI 解析 | 0 (根) |
| **Gateway** | `src/gateway/` | WebSocket 服务器、会话管理 | 1 |
| **Agents** | `src/agents/` | AI 代理执行、模型调用 | 2 |
| **ACP** | `src/acp/` | 代理协议、进程间通信 | 2 |
| **Plugins** | `src/plugins/` | 插件生命周期 | 1 |
| **Channels** | `src/channels/` | 消息渠道抽象 | 2 |
| **Config** | `src/config/` | 配置加载验证 | 0 |
| **Sessions** | `src/sessions/` | 会话状态持久化 | 1 |
| **Security** | `src/security/` | 认证授权、沙箱 | 1 |
| **CLI** | `src/cli/` | 命令行界面 | 1 |

### 5.2 扩展系统

项目支持 70+ 扩展，分为以下类别：

**模型提供商 (35+):**
- `anthropic` - Claude 模型
- `openai` - GPT/Codex 模型
- `google` - Gemini 模型
- `mistral` - Mistral 模型
- `groq` - Groq 模型
- `ollama` - 本地模型
- `openrouter` - 多模型网关
- `deepseek` - DeepSeek 模型
- `amazon-bedrock` - AWS Bedrock
- ...

**消息渠道 (20+):**
- `telegram` - Telegram Bot
- `discord` - Discord Bot
- `slack` - Slack App
- `whatsapp` - WhatsApp (Baileys)
- `signal` - Signal
- `matrix` - Matrix
- `msteams` - Microsoft Teams
- `feishu` - 飞书
- `line` - LINE
- `irc` - IRC
- ...

**功能扩展 (15+):**
- `memory-core` - 内存/上下文存储
- `memory-lancedb` - LanceDB 向量存储
- `brave` - Brave 搜索
- `tavily` - Tavily 搜索
- `elevenlabs` - 语音合成
- `deepgram` - 语音识别
- `firecrawl` - 网页爬取
- ...

---

## 6. 数据流概述

### 6.1 主数据流

```
用户消息 (WhatsApp/Telegram/etc.)
 │
 ▼
渠道适配器 (extensions/telegram/)
 │ 解析消息格式
 ▼
Gateway (src/gateway/)
 │ 认证 + 路由
 ▼
会话管理 (src/sessions/)
 │ 加载会话状态
 ▼
Agent Runtime (src/agents/)
 │ 构建提示词 + 调用模型
 ▼
模型提供商 (extensions/anthropic/)
 │ API 调用
 ▼
响应流 (SSE/WebSocket)
 │ 流式返回
 ▼
渠道适配器
 │ 格式化响应
 ▼
用户接收消息
```

### 6.2 工具执行流

```
Agent 决定调用工具
 │
 ▼
工具注册表 (src/plugins/)
 │ 查找工具实现
 ▼
权限检查 (src/security/)
 │ 验证执行权限
 ▼
工具执行
 │ 可能是：
 │ - 本地命令 (bash)
 │ - 浏览器操作 (browser)
 │ - 消息发送 (message)
 │ - 设备操作 (node.invoke)
 ▼
结果返回给 Agent
```

---

## 7. 外部集成与依赖

### 7.1 模型提供商

| 提供商 | 认证方式 | 特性 |
|--------|---------|------|
| Anthropic | API Key / OAuth | Claude 模型，扩展思考 |
| OpenAI | API Key / OAuth | GPT/Codex，函数调用 |
| Google | API Key / OAuth | Gemini，多模态 |
| Mistral | API Key | Mistral 模型 |
| Groq | API Key | 高速推理 |
| Ollama | 本地 | 本地模型运行 |
| OpenRouter | API Key | 多模型网关 |

### 7.2 消息渠道

| 渠道 | 协议 | 特性 |
|------|------|------|
| Telegram | Bot API | Webhook/Polling |
| Discord | Gateway WebSocket | Slash 命令 |
| Slack | Bolt SDK | App Home, Modals |
| WhatsApp | Baileys (非官方) | QR 码登录 |
| Signal | signal-cli | 需要 signal-cli |
| Matrix | Matrix SDK | 联邦协议 |
| iMessage | BlueBubbles / imsg | macOS 专属 |

### 7.3 第三方服务

| 服务 | 用途 | 必需性 |
|------|------|--------|
| Tailscale | 远程访问 | 可选 |
| ElevenLabs | 语音合成 | 可选 |
| Deepgram | 语音识别 | 可选 |
| Brave Search | 网页搜索 | 可选 |
| ClawHub | 技能市场 | 可选 |

---

## 8. TL;DR (执行摘要)

### 关键发现

1. **项目规模庞大**：1000+ TypeScript 文件，70+ 扩展包，完整的 monorepo 结构
2. **架构清晰**：Gateway 作为控制平面，Agent 作为执行引擎，Plugins 提供扩展性
3. **生产就绪**：完整的 CI/CD、测试覆盖、文档体系
4. **活跃社区**：20+ 核心维护者，定期发布，活跃的 Discord 社区
5. **技术前沿**：采用最新的 TypeScript 5.9、Node.js 24、ACP/MCP 协议