# 天一阁架构文档 v3.0.13

**版本**: v3.0.13
**日期**: 2026-03-30
**主题**: 移动端适配 + AI 辅助写作 + 知识图谱可视化 + 高级权限管理 + 数据备份与恢复

---

## 📋 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0.13 | 2026-03-30 | 移动端架构 + AI 写作架构 + 知识图谱架构 + 权限架构 + 备份架构 |
| v3.0.12 | 2026-03-29 | LibIndex One 同步架构 + 项目管理架构 + 协作架构 + 插件架构 |
| v3.0.11 | 2026-03-29 | 前端认证架构 + 向量搜索架构 + 批量操作架构 |

---

## 🏗️ 系统架构总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           前端层 (React + PWA)                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Mobile UI   │  AI Writing   │  Knowledge Graph  │  Permissions  │ Backup │
│  - Responsive│  - Assistant  │  - Visualization  │  - Roles      │ - UI   │
│  - Touch     │  - Grammar    │  - Navigator      │  - Policies   │        │
│  - PWA       │  - Translate  │  - Explorer       │  - Audit      │        │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────────┐
│                           API 层 (FastAPI)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  /mobile     │  /ai-writing  │  /knowledge-graph │  /permissions │ /backup│
│  - Detect    │  - continue   │  - nodes/edges    │  - check      │ - jobs │
│  - Manifest  │  - polish     │  - search         │  - roles      │ - restore
└─────────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────────┐
│                        服务层 (Services)                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  MobileAdapter      │  AIWritingService      │  KnowledgeGraphService    │
│  - Breakpoint       │  - Continue            │  - GraphBuilder           │
│  - TouchHandler     │  - Polish              │  - LayoutEngine           │
│  - PWAConfig        │  - GrammarCheck        │  - Navigator              │
├─────────────────────────────────────────────────────────────────────────┤
│  PermissionService  │  BackupService                                     │
│  - RBAC             │  - Full/Incremental                                │
│  - ABAC             │  - Compression                                     │
│  - Audit            │  - Encryption                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────────┐
│                        数据层                                             │
├─────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis         │  Object Storage      │  Vector DB       │
│  - roles     │  - permissions │  - backup archives   │  - graph cache   │
│  - policies  │  - cache       │  - attachments       │                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 一、移动端适配架构

### 1.1 响应式架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      ResponsiveContainer                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐   ┌─────────────────┐   ┌─────────────────┐  │
│   │   Mobile    │   │     Tablet      │   │    Desktop      │  │
│   │   (<768px)  │   │   (768-1024px)  │   │   (>1024px)     │  │
│   │             │   │                 │   │                 │  │
│   │ ┌─────────┐ │   │ ┌─────┐┌──────┐ │   │ ┌───┐┌───┐┌───┐ │  │
│   │ │  Nav    │ │   │ │Nav  ││Main  │ │   │ │Nav││Main││Side│ │  │
│   │ ├─────────┤ │   │ └─────┘└──────┘ │   │ └───┘└───┘└───┘ │  │
│   │ │  Main   │ │   │                 │   │                 │  │
│   │ ├─────────┤ │   │                 │   │                 │  │
│   │ │BottomBar│ │   │                 │   │                 │  │
│   │ └─────────┘ │   │                 │   │                 │  │
│   │             │   │                 │   │                 │  │
│   └─────────────┘   └─────────────────┘   └─────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 PWA 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        PWA Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Service Worker                                                │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │  Cache      │  │  Background │  │  Push       │     │  │
│   │  │  Strategy   │  │  Sync       │  │  Notification│     │  │
│   │  │             │  │             │  │             │     │  │
│   │  │ - Static    │  │ - Queue     │  │ - Web Push  │     │  │
│   │  │ - API       │  │ - Retry     │  │ - Local     │     │  │
│   │  │ - Images    │  │ - Offline   │  │             │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   Web App Manifest                                           │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  name, short_name, icons, start_url, display, theme   │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   Browser UI Components                                       │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │  Add to Home Screen │ Splash Screen │ Offline Page     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 触摸交互架构

```typescript
// hooks/useTouch.ts
interface TouchHandler {
  onTouchStart: (e: TouchEvent) => void;
  onTouchMove: (e: TouchEvent) => void;
  onTouchEnd: (e: TouchEvent) => void;
  gesture: GestureState;
}

interface GestureState {
  type: 'tap' | 'swipe' | 'pinch' | 'rotate' | 'pan' | null;
  direction: 'left' | 'right' | 'up' | 'down' | null;
  distance: number;
  velocity: number;
  scale: number;
  rotation: number;
}
```

---

## 🤖 二、AI 辅助写作架构

### 2.1 AI 写作服务架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      AI Writing Service                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                    WritingEngine                         │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │  Continue   │  │   Polish    │  │   Summary   │     │  │
│   │  │             │  │             │  │             │     │  │
│   │  │ - Context   │  │ - Tone      │  │ - Extract   │     │  │
│   │  │ - Generate  │  │ - Style     │  │ - Condense  │     │  │
│   │  │ - Suggest   │  │ - Improve   │  │ - TL;DR     │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │   Expand    │  │  Translate  │  │    Tone     │     │  │
│   │  │             │  │             │  │             │     │  │
│   │  │ - Elaborate │  │ - Multi-lang│  │ - Convert   │     │  │
│   │  │ - Examples  │  │ - Preserve  │  │ - Adjust    │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                  GrammarChecker                          │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │   Spell     │  │   Grammar   │  │    Style    │     │  │
│   │  │   Check     │  │   Check     │  │    Check    │     │  │
│   │  │             │  │             │  │             │     │  │
│   │  │ - Dictionary│  │ - Rules     │  │ - Clarity   │     │  │
│   │  │ - ML Model  │  │ - ML Model  │  │ - Readability│     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                      LLM Client                          │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │  OpenAI     │  │  Anthropic  │  │  Local LLM  │     │  │
│   │  │  GPT-4      │  │  Claude     │  │  (Optional) │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 写作上下文管理

```typescript
// services/ai/ContextManager.ts
interface WritingContext {
  documentId: string;
  cursorPosition: number;
  selectionRange?: { start: number; end: number };
  documentContent: string;
  documentType: 'article' | 'report' | 'note' | 'code';
  recentEdits: EditHistory[];
  userPreferences: UserWritingPreferences;
}

interface ContextProvider {
  getContext(): Promise<WritingContext>;
  updateContext(update: Partial<WritingContext>): void;
  getRelevantSnippets(query: string, limit: number): Promise<string[]>;
}
```

---

## 🕸️ 三、知识图谱可视化架构

### 3.1 知识图谱构建流程

```
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Graph Builder                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Input Documents                                                │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────┐                                                │
│   │  Text       │                                                │
│   │  Preprocess │                                                │
│   │  - Tokenize │                                                │
│   │  - Clean    │                                                │
│   └──────┬──────┘                                                │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│   │  Entity     │────▶│  Relation   │────▶│  Graph      │       │
│   │  Extraction │     │  Extraction │     │  Construction│      │
│   │             │     │             │     │             │       │
│   │ - NER       │     │ - Co-occur  │     │ - Node/Edge │       │
│   │ - Coref     │     │ - Semantic  │     │ - Embedding │       │
│   │ - Keywords  │     │ - Citation  │     │ - Cluster   │       │
│   └─────────────┘     └─────────────┘     └─────────────┘       │
│          │                              │                        │
│          ▼                              ▼                        │
│   ┌─────────────┐                ┌─────────────┐                │
│   │  Vector DB  │                │  Graph DB   │                │
│   │  (Qdrant)   │                │  (Neo4j)    │                │
│   └─────────────┘                └─────────────┘                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 图谱可视化引擎

```
┌─────────────────────────────────────────────────────────────────┐
│                    Graph Visualization Engine                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   Layout Algorithms                      │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │   Force     │  │  Hierarchical│  │   Circular  │     │  │
│   │  │   Directed  │  │   Layout    │  │   Layout    │     │  │
│   │  │             │  │             │  │             │     │  │
│   │  │ - D3 Force  │  │ - Tree      │  │ - Radial    │     │  │
│   │  │ - G6 Force  │  │ - Dagre     │  │ - Chord     │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   Rendering Layer                        │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │   Canvas    │  │    SVG      │  │    WebGL    │     │  │
│   │  │  (2D)       │  │  (Vector)   │  │  (GPU)      │     │  │
│   │  │             │  │             │  │             │     │  │
│   │  │ - Large     │  │ - Interactive│  │ - Massive   │     │  │
│   │  │   Graphs    │  │   Events    │  │   Graphs    │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   Interaction Layer                      │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │   Zoom      │  │   Pan       │  │   Select    │     │  │
│   │  │   Hover     │  │   Drag      │  │   Filter    │     │  │
│   │  │   Click     │  │   Expand    │  │   Search    │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.3 知识导航服务

```typescript
// services/knowledge/KnowledgeNavigator.ts
interface NavigationPath {
  nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
  relevance: number;
}

interface KnowledgeNavigator {
  findPath(start: string, end: string): Promise<NavigationPath>;
  getRelatedDocuments(documentId: string, limit: number): Promise<Document[]>;
  getDocumentCluster(documentId: string): Promise<KnowledgeNode[]>;
  exploreNeighborhood(
    nodeId: string,
    depth: number
  ): Promise<{ nodes: KnowledgeNode[]; edges: KnowledgeEdge[] }>;
}
```

---

## 🔐 四、高级权限管理架构

### 4.1 权限模型架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Permission Architecture                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   Policy Decision Point                  │  │
│   │                                                          │  │
│   │   Subject (User/Group) + Resource + Action + Context    │  │
│   │              │                                           │  │
│   │              ▼                                           │  │
│   │   ┌─────────────────────────────────────────────────┐   │  │
│   │   │         Policy Evaluation Engine                │   │  │
│   │   │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │   │  │
│   │   │  │   Role      │  │  Resource   │  │  ABAC   │ │   │  │
│   │   │  │   Policies  │  │   Policies  │  │  Rules  │ │   │  │
│   │   │  └─────────────┘  └─────────────┘  └─────────┘ │   │  │
│   │   └─────────────────────────────────────────────────┘   │  │
│   │              │                                           │  │
│   │              ▼                                           │  │
│   │         Decision: Allow / Deny                           │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   Policy Administration                  │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │   Role      │  │   Policy    │  │   Audit     │     │  │
│   │  │   Manager   │  │   Editor    │  │   Logger    │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 RBAC + ABAC 混合模型

```typescript
// models/permissions.ts
interface RBACModel {
  roles: Role[];
  roleAssignments: Array<{
    userId: string;
    roleId: string;
    scope?: string; // project/org level
  }>;
}

interface ABACModel {
  policies: Array<{
    id: string;
    subject: string; // user/group pattern
    resource: string; // resource pattern
    action: string; // action pattern
    effect: 'allow' | 'deny';
    conditions?: {
      timeOfDay?: { start: string; end: string };
      dayOfWeek?: number[];
      ipRange?: string[];
      mfaVerified?: boolean;
      customAttributes?: Record<string, any>;
    };
  }>;
}

interface PermissionService {
  checkPermission(
    subject: string,
    resource: string,
    action: string,
    context: PermissionContext
  ): Promise<boolean>;
  
  listPermissions(subject: string): Promise<Permission[]>;
  grantPermission(policy: Policy): Promise<void>;
  revokePermission(policyId: string): Promise<void>;
}
```

### 4.3 权限缓存架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Permission Cache                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Request ─────▶ Check Cache                                     │
│                     │                                            │
│              ┌────┴────┐                                         │
│              │  Hit?   │                                         │
│              └────┬────┘                                         │
│             Yes   │   No                                         │
│                   │                                              │
│              Return │  Evaluate                                    │
│                     │       │                                      │
│                     │       ▼                                      │
│                     │  Store in                                    │
│                     │  Cache (TTL)                                 │
│                     │       │                                      │
│                     └───────┘                                      │
│                                                                  │
│   Cache Structure:                                               │
│   Key: perm:{userId}:{resource}:{action}                         │
│   Value: { allowed: boolean, expires: timestamp }                │
│   TTL: 5 minutes                                                 │
│                                                                  │
│   Invalidation:                                                  │
│   - On policy change                                             │
│   - On role change                                               │
│   - On permission grant/revoke                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💾 五、数据备份与恢复架构

### 5.1 备份系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Backup System Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   Backup Scheduler                       │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │   Daily     │  │   Weekly    │  │   Monthly   │     │  │
│   │  │   Full      │  │   Full      │  │   Full      │     │  │
│   │  │             │  │             │  │             │     │  │
│   │  │ 02:00 UTC   │  │ Sun 02:00   │  │ 1st 02:00   │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   Backup Job Runner                      │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │   Full      │  │  Incremental│  │   Snapshot  │     │  │
│   │  │   Backup    │  │   Backup    │  │   Backup    │     │  │
│   │  │             │  │             │  │             │     │  │
│   │  │ - Database  │  │ - Change    │  │ - Volume    │     │  │
│   │  │ - Files     │  │   detection │  │   snapshot  │     │  │
│   │  │ - Vectors   │  │ - Delta     │  │             │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                              │                                   │
│   ┌─────────────────────────────────────────────────────────┐  │
│   │                   Storage Destinations                   │  │
│   │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │  │
│   │  │    Local    │  │     S3      │  │    GCS      │     │  │
│   │  │   (SSD)     │  │  (Primary)  │  │ (Secondary) │     │  │
│   │  └─────────────┘  └─────────────┘  └─────────────┘     │  │
│   └─────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 增量备份流程

```
┌─────────────────────────────────────────────────────────────────┐
│                   Incremental Backup Flow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Check Last Backup                                           │
│        │                                                         │
│        ▼                                                         │
│   2. Detect Changes                                              │
│      ├─ Database: Compare checksums or use WAL                   │
│      ├─ Files: Compare timestamps + checksums                    │
│      └─ Vectors: Track update timestamps                         │
│        │                                                         │
│        ▼                                                         │
│   3. Export Changed Data                                         │
│      ├─ pg_dump --data-only --inserts                            │
│      ├─ rsync --checksum                                         │
│      └─ Vector DB export                                         │
│        │                                                         │
│        ▼                                                         │
│   4. Compress (gzip/zstd)                                        │
│        │                                                         │
│        ▼                                                         │
│   5. Encrypt (AES-256)                                           │
│        │                                                         │
│        ▼                                                         │
│   6. Upload to Storage                                           │
│        │                                                         │
│        ▼                                                         │
│   7. Update Backup Manifest                                      │
│        │                                                         │
│        ▼                                                         │
│   8. Cleanup Old Backups (retention policy)                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 恢复流程

```
┌─────────────────────────────────────────────────────────────────┐
│                     Restore Flow                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Select Restore Point                                        │
│        │                                                         │
│        ▼                                                         │
│   2. Pre-flight Checks                                           │
│      ├─ Verify backup integrity                                  │
│      ├─ Check storage space                                      │
│      └─ Validate backup format                                   │
│        │                                                         │
│        ▼                                                         │
│   3. Download Backup                                             │
│        │                                                         │
│        ▼                                                         │
│   4. Decrypt                                                     │
│        │                                                         │
│        ▼                                                         │
│   5. Decompress                                                  │
│        │                                                         │
│        ▼                                                         │
│   6. Restore Order                                               │
│      ├─ 1. Database schema (if needed)                           │
│      ├─ 2. Database data                                         │
│      ├─ 3. File attachments                                       │
│      ├─ 4. Vector indices                                         │
│      └─ 5. Search indices                                         │
│        │                                                         │
│        ▼                                                         │
│   7. Verify Restore                                              │
│      ├─ Row counts match                                         │
│      ├─ File checksums match                                     │
│      └─ Application smoke test                                   │
│        │                                                         │
│        ▼                                                         │
│   8. Update Recovery Point Objective (RPO) metrics               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 灾难恢复架构

```
┌─────────────────────────────────────────────────────────────────┐
│                 Disaster Recovery Architecture                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Primary Region                    Secondary Region            │
│   ┌───────────────┐                ┌───────────────┐           │
│   │  Application  │───────────────▶│  Standby App  │           │
│   │   Servers     │   Replication  │   Servers     │           │
│   └───────┬───────┘                └───────┬───────┘           │
│           │                                │                    │
│   ┌───────▼───────┐                ┌───────▼───────┐           │
│   │   Primary DB  │◀──────────────▶│  Replica DB   │           │
│   │  (PostgreSQL) │   Streaming    │  (PostgreSQL) │           │
│   └───────┬───────┘   Replication  └───────┬───────┘           │
│           │                                │                    │
│   ┌───────▼───────┐                ┌───────▼───────┐           │
│   │  Object Store │◀──────────────▶│ Object Store  │           │
│   │    (S3)       │   Cross-Region │    (S3)       │           │
│   └───────────────┘   Replication  └───────────────┘           │
│                                                                  │
│   Failover:                                                      │
│   1. Detect primary failure                                      │
│   2. Promote secondary DB                                        │
│   3. Route traffic to secondary                                  │
│   4. Restore primary when available                              │
│                                                                  │
│   RPO: < 5 minutes                                               │
│   RTO: < 15 minutes                                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 数据模型

### 6.1 权限相关表

```sql
-- 角色表
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]',
    inherits UUID[],
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 权限策略表
CREATE TABLE permission_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    subject VARCHAR(255) NOT NULL, -- user_id or group pattern
    resource VARCHAR(255) NOT NULL, -- resource pattern
    action VARCHAR(100) NOT NULL,
    effect VARCHAR(10) NOT NULL CHECK (effect IN ('allow', 'deny')),
    conditions JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 审计日志表
CREATE TABLE permission_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(255) NOT NULL,
    decision BOOLEAN NOT NULL,
    context JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 备份相关表

```sql
-- 备份任务表
CREATE TABLE backup_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(20) NOT NULL CHECK (type IN ('full', 'incremental')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    size_bytes BIGINT,
    file_count INTEGER,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 备份配置表
CREATE TABLE backup_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    schedule VARCHAR(20) NOT NULL,
    backup_time TIME NOT NULL,
    retention_days INTEGER NOT NULL DEFAULT 30,
    destinations JSONB NOT NULL,
    include_attachments BOOLEAN DEFAULT true,
    compression_level VARCHAR(10) DEFAULT 'fast',
    encryption_enabled BOOLEAN DEFAULT true,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 恢复任务表
CREATE TABLE restore_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    backup_job_id UUID REFERENCES backup_jobs(id),
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.3 知识图谱相关表

```sql
-- 知识节点表
CREATE TABLE knowledge_nodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(50) NOT NULL,
    label VARCHAR(255) NOT NULL,
    properties JSONB DEFAULT '{}',
    embedding VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 知识边表
CREATE TABLE knowledge_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID NOT NULL REFERENCES knowledge_nodes(id),
    target_id UUID NOT NULL REFERENCES knowledge_nodes(id),
    type VARCHAR(50) NOT NULL,
    label VARCHAR(255),
    weight FLOAT DEFAULT 1.0,
    properties JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW()
);

-- 节点-文档关联表
CREATE TABLE node_document_mappings (
    node_id UUID REFERENCES knowledge_nodes(id),
    document_id UUID REFERENCES documents(id),
    confidence FLOAT DEFAULT 1.0,
    PRIMARY KEY (node_id, document_id)
);
```

---

## 🔧 API 设计

### 7.1 移动端适配 API

```yaml
# Mobile Detection & PWA
GET /api/v1/mobile/detect:
  description: 检测设备类型和特性
  response:
    isMobile: boolean
    screenSize: { width: number, height: number }
    touchEnabled: boolean
    orientation: 'portrait' | 'landscape'

GET /api/v1/mobile/manifest.json:
  description: PWA manifest 文件
  response: WebAppManifest

POST /api/v1/mobile/subscribe-push:
  description: 订阅推送通知
  body:
    endpoint: string
    keys: { p256dh: string, auth: string }
```

### 7.2 AI 写作 API

```yaml
# AI Writing
POST /api/v1/ai/continue:
  description: 续写内容
  body:
    context: string
    cursorPosition: number
    tone: string
    maxLength: number
  response:
    content: string
    suggestions: string[]
    confidence: number

POST /api/v1/ai/polish:
  description: 润色文本
  body:
    text: string
    tone: 'professional' | 'casual' | 'academic'
  response:
    content: string
    changes: Array<{ original: string, replacement: string }>

POST /api/v1/ai/grammar-check:
  description: 语法检查
  body:
    text: string
  response:
    issues: Array<{
      start: number
      end: number
      type: 'grammar' | 'spelling' | 'style'
      message: string
      suggestion: string
    }>
```

### 7.3 知识图谱 API

```yaml
# Knowledge Graph
GET /api/v1/knowledge/graph:
  description: 获取知识图谱
  query:
    documentIds: string[]
    depth: number
  response:
    nodes: KnowledgeNode[]
    edges: KnowledgeEdge[]

GET /api/v1/knowledge/nodes/{id}/related:
  description: 获取相关节点
  response:
    nodes: KnowledgeNode[]
    path: KnowledgeEdge[]

GET /api/v1/knowledge/search:
  description: 在知识图谱中搜索
  query:
    q: string
    type: 'node' | 'edge' | 'path'
  response:
    results: Array<KnowledgeNode | KnowledgeEdge | NavigationPath>

GET /api/v1/knowledge/documents/{id}/navigate:
  description: 文档知识导航
  response:
    relatedDocuments: Document[]
    knowledgePath: KnowledgeNode[]
```

### 7.4 权限管理 API

```yaml
# Permissions
GET /api/v1/permissions/check:
  description: 检查权限
  query:
    resource: string
    action: string
  response:
    allowed: boolean
    reason: string

GET /api/v1/roles:
  description: 列出角色
  response:
    roles: Role[]

POST /api/v1/roles:
  description: 创建角色
  body: Role
  response: Role

PUT /api/v1/roles/{id}:
  description: 更新角色
  body: Partial<Role>
  response: Role

DELETE /api/v1/roles/{id}:
  description: 删除角色

GET /api/v1/permissions/policies:
  description: 列出权限策略
  response:
    policies: Policy[]

POST /api/v1/permissions/policies:
  description: 创建权限策略
  body: Policy
  response: Policy

GET /api/v1/permissions/audit:
  description: 权限审计日志
  query:
    userId: string
    startDate: string
    endDate: string
  response:
    logs: AuditLog[]
```

### 7.5 备份恢复 API

```yaml
# Backup & Restore
GET /api/v1/backups:
  description: 列出备份
  response:
    backups: BackupJob[]

POST /api/v1/backups:
  description: 创建备份
  body:
    type: 'full' | 'incremental'
  response: BackupJob

GET /api/v1/backups/{id}:
  description: 获取备份详情
  response: BackupJob

DELETE /api/v1/backups/{id}:
  description: 删除备份

POST /api/v1/backups/{id}/restore:
  description: 从备份恢复
  response: RestoreJob

GET /api/v1/backups/config:
  description: 获取备份配置
  response: BackupConfig

PUT /api/v1/backups/config:
  description: 更新备份配置
  body: BackupConfig
  response: BackupConfig

GET /api/v1/backups/restore-jobs:
  description: 列出恢复任务
  response:
    jobs: RestoreJob[]
```

---

## 📈 性能考虑

### 8.1 移动端性能优化

| 优化项 | 策略 | 目标 |
|--------|------|------|
| 代码分割 | 路由级懒加载 | FCP < 1.5s |
| 图片优化 | WebP + 响应式图片 | LCP < 2.5s |
| 缓存策略 | Service Worker | 离线可用 |
| 触摸响应 | 16ms 帧率 | 流畅交互 |

### 8.2 AI 写作性能

| 优化项 | 策略 | 目标 |
|--------|------|------|
| 响应延迟 | 流式输出 | TTFB < 500ms |
| 并发控制 | 请求队列 | 避免限流 |
| 缓存 | 提示词缓存 | 重复请求优化 |
| 预加载 | 模型预热 | 首次响应优化 |

### 8.3 知识图谱性能

| 优化项 | 策略 | 目标 |
|--------|------|------|
| 渲染性能 | WebGL + 节点合并 | 1000+ 节点流畅 |
| 查询性能 | 预计算 + 缓存 | 查询 < 100ms |
| 布局算法 | Web Worker | 不阻塞主线程 |
| 增量更新 | 局部重渲染 | 快速响应 |

### 8.4 权限检查性能

| 优化项 | 策略 | 目标 |
|--------|------|------|
| 缓存 | Redis 缓存 | 检查 < 10ms |
| 批量检查 | 单次请求多权限 | 减少往返 |
| 预加载 | 会话启动加载 | 实时检查优化 |
| 增量更新 | 变更时刷新 | 避免全量重载 |

### 8.5 备份恢复性能

| 优化项 | 策略 | 目标 |
|--------|------|------|
| 压缩 | zstd 并行压缩 | 速度 vs 比率平衡 |
| 分片上传 | 100MB 分片 | 大文件支持 |
| 并行处理 | 多表并发 | 备份速度优化 |
| 增量检测 | 校验和比较 | 减少传输量 |

---

## 🔒 安全考虑

### 9.1 移动端安全

- **PWA 安全**: HTTPS 强制, Service Worker 完整性校验
- **本地存储**: 敏感数据加密存储
- **触摸安全**: 防误触, 手势确认

### 9.2 AI 写作安全

- **输入过滤**: 防止提示词注入
- **输出审查**: 敏感内容过滤
- **审计日志**: 记录 AI 交互

### 9.3 知识图谱安全

- **数据隔离**: 用户数据边界
- **查询限制**: 复杂度限制防 DoS
- **权限集成**: 节点级权限控制

### 9.4 权限安全

- **最小权限**: 默认拒绝
- **权限审查**: 定期审计
- **异常检测**: 异常访问告警

### 9.5 备份安全

- **传输加密**: TLS 1.3
- **存储加密**: AES-256-GCM
- **密钥管理**: 硬件安全模块 (HSM)
- **访问控制**: 备份下载需 MFA

---

## 📊 版本总结

### v3.0.13 架构交付清单

| 模块 | 架构设计 | 数据模型 | API 设计 | 性能优化 |
|------|----------|----------|----------|----------|
| 移动端适配 | ✅ | N/A | ✅ | ✅ |
| AI 辅助写作 | ✅ | N/A | ✅ | ✅ |
| 知识图谱可视化 | ✅ | ✅ | ✅ | ✅ |
| 高级权限管理 | ✅ | ✅ | ✅ | ✅ |
| 数据备份与恢复 | ✅ | ✅ | ✅ | ✅ |

### 下一步架构规划 (v3.0.14)

- [ ] 推荐系统架构
- [ ] 文档版本对比引擎
- [ ] 工作流编排引擎
- [ ] 高级分析架构
- [ ] 多语言架构

---

**更新时间**: 2026-03-30 23:00
