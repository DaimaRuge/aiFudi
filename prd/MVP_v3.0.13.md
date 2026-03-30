# 天一阁 PRD v3.0.13

**版本**: v3.0.13
**日期**: 2026-03-30
**阶段**: 移动端适配 + AI 辅助写作 + 知识图谱可视化 + 高级权限管理 + 数据备份与恢复

---

## 📋 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0.13 | 2026-03-30 | 移动端适配 + AI 辅助写作 + 知识图谱可视化 + 高级权限管理 + 数据备份与恢复 |
| v3.0.12 | 2026-03-29 | LibIndex One 同步服务 + 项目级管理 + 协作功能 + 插件系统 |
| v3.0.11 | 2026-03-28 | 用户认证界面 + 向量搜索集成 + 高级搜索 + 批量操作 + 导入导出 |

---

## 🎯 本次迭代目标

### 核心交付物
- [ ] **移动端适配**: 响应式布局、PWA 支持、移动端优化交互
- [ ] **AI 辅助写作**: 智能续写、内容优化、风格转换、语法检查
- [ ] **知识图谱可视化**: 实体关系图、知识导航、图谱探索
- [ ] **高级权限管理**: 细粒度权限、权限继承、临时授权
- [ ] **数据备份与恢复**: 自动备份、增量备份、跨地域恢复

---

## ✅ 一、移动端适配

### 1.1 响应式布局架构

```typescript
// hooks/useBreakpoint.ts
export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl' | 'xxl';

export interface BreakpointConfig {
  xs: number;  // < 576px
  sm: number;  // >= 576px
  md: number;  // >= 768px
  lg: number;  // >= 992px
  xl: number;  // >= 1200px
  xxl: number; // >= 1400px
}

export const useBreakpoint = (): Breakpoint => {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('lg');
  
  useEffect(() => {
    const updateBreakpoint = () => {
      const width = window.innerWidth;
      if (width < 576) setBreakpoint('xs');
      else if (width < 768) setBreakpoint('sm');
      else if (width < 992) setBreakpoint('md');
      else if (width < 1200) setBreakpoint('lg');
      else if (width < 1400) setBreakpoint('xl');
      else setBreakpoint('xxl');
    };
    
    updateBreakpoint();
    window.addEventListener('resize', updateBreakpoint);
    return () => window.removeEventListener('resize', updateBreakpoint);
  }, []);
  
  return breakpoint;
};

// components/ResponsiveContainer.tsx
export interface ResponsiveContainerProps {
  children: React.ReactNode;
  mobileLayout?: React.ReactNode;
  tabletLayout?: React.ReactNode;
  desktopLayout?: React.ReactNode;
}

export const ResponsiveContainer: React.FC<ResponsiveContainerProps> = ({
  children,
  mobileLayout,
  tabletLayout,
  desktopLayout
}) => {
  const breakpoint = useBreakpoint();
  const isMobile = ['xs', 'sm'].includes(breakpoint);
  const isTablet = breakpoint === 'md';
  
  if (isMobile && mobileLayout) return <>{mobileLayout}</>;
  if (isTablet && tabletLayout) return <>{tabletLayout}</>;
  if (desktopLayout) return <>{desktopLayout}</>;
  
  return <>{children}</>;
};
```

### 1.2 移动端组件库

```typescript
// components/mobile/MobileNavbar.tsx
export interface MobileNavbarProps {
  title: string;
  onBack?: () => void;
  rightActions?: React.ReactNode;
}

export const MobileNavbar: React.FC<MobileNavbarProps> = ({
  title,
  onBack,
  rightActions
}) => {
  return (
    <div className="mobile-navbar">
      {onBack && (
        <Button icon={<LeftOutlined />} onClick={onBack} type="text" />
      )}
      <span className="mobile-navbar-title">{title}</span>
      {rightActions && <div className="mobile-navbar-actions">{rightActions}</div>}
    </div>
  );
};

// components/mobile/MobileDrawer.tsx
export interface MobileDrawerProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  placement?: 'bottom' | 'left' | 'right' | 'top';
  height?: number | string;
}

export const MobileDrawer: React.FC<MobileDrawerProps> = ({
  visible,
  onClose,
  title,
  children,
  placement = 'bottom',
  height = '80%'
}) => {
  return (
    <Drawer
      open={visible}
      onClose={onClose}
      title={title}
      placement={placement}
      height={placement === 'bottom' || placement === 'top' ? height : undefined}
      className="mobile-drawer"
      destroyOnClose
    >
      {children}
    </Drawer>
  );
};

// components/mobile/MobileSearch.tsx
export interface MobileSearchProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  onCancel?: () => void;
  autoFocus?: boolean;
}

export const MobileSearch: React.FC<MobileSearchProps> = ({
  placeholder = '搜索...',
  onSearch,
  onCancel,
  autoFocus = true
}) => {
  const [query, setQuery] = useState('');
  
  return (
    <div className="mobile-search">
      <SearchOutlined />
      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        onPressEnter={() => onSearch(query)}
      />
      {query && (
        <CloseOutlined onClick={() => { setQuery(''); onCancel?.(); }} />
      )}
    </div>
  );
};
```

### 1.3 PWA 配置

```typescript
// vite.config.ts PWA 配置
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: '天一阁',
        short_name: '天一阁',
        description: '智能知识管理系统',
        theme_color: '#1890ff',
        background_color: '#ffffff',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          { src: '/icon-192x192.png', sizes: '192x192', type: 'image/png' },
          { src: '/icon-512x512.png', sizes: '512x512', type: 'image/png' },
          { src: '/icon-maskable.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\./,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 86400 }
            }
          },
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'image-cache',
              expiration: { maxEntries: 200, maxAgeSeconds: 604800 }
            }
          }
        ]
      }
    })
  ]
});
```

### 1.4 移动端触摸交互优化

```typescript
// hooks/useTouch.ts
export interface TouchState {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  direction: 'left' | 'right' | 'up' | 'down' | null;
  distance: number;
}

export const useTouch = (options?: {
  threshold?: number;
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
}) => {
  const [touchState, setTouchState] = useState<TouchState | null>(null);
  
  const onTouchStart = (e: TouchEvent) => {
    const touch = e.touches[0];
    setTouchState({
      startX: touch.clientX,
      startY: touch.clientY,
      endX: touch.clientX,
      endY: touch.clientY,
      direction: null,
      distance: 0
    });
  };
  
  const onTouchEnd = (e: TouchEvent) => {
    if (!touchState) return;
    
    const touch = e.changedTouches[0];
    const endX = touch.clientX;
    const endY = touch.clientY;
    
    const deltaX = endX - touchState.startX;
    const deltaY = endY - touchState.startY;
    const threshold = options?.threshold || 50;
    
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > threshold) {
      if (deltaX > 0) {
        options?.onSwipeRight?.();
      } else {
        options?.onSwipeLeft?.();
      }
    } else if (Math.abs(deltaY) > threshold) {
      if (deltaY > 0) {
        options?.onSwipeDown?.();
      } else {
        options?.onSwipeUp?.();
      }
    }
    
    setTouchState(null);
  };
  
  return { onTouchStart, onTouchEnd, touchState };
};

// components/SwipeableList.tsx
export interface SwipeableListProps {
  items: Array<{ id: string; content: React.ReactNode }>;
  onSwipeLeft?: (id: string) => void;
  onSwipeRight?: (id: string) => void;
  renderActions?: (id: string, direction: 'left' | 'right') => React.ReactNode;
}

export const SwipeableList: React.FC<SwipeableListProps> = ({
  items,
  onSwipeLeft,
  onSwipeRight,
  renderActions
}) => {
  return (
    <List className="swipeable-list">
      {items.map(item => (
        <SwipeableItem
          key={item.id}
          id={item.id}
          content={item.content}
          onSwipeLeft={() => onSwipeLeft?.(item.id)}
          onSwipeRight={() => onSwipeRight?.(item.id)}
          renderActions={renderActions}
        />
      ))}
    </List>
  );
};
```

---

## ✅ 二、AI 辅助写作

### 2.1 AI 写作引擎架构

```typescript
// services/ai/AIWritingService.ts
export interface AIWritingOptions {
  mode: 'continue' | 'polish' | 'translate' | 'summary' | 'expand';
  tone?: 'professional' | 'casual' | 'academic' | 'creative';
  language?: string;
  maxLength?: number;
}

export interface AIWritingResult {
  content: string;
  suggestions: string[];
  confidence: number;
  alternatives?: string[];
}

export class AIWritingService {
  constructor(
    private llmClient: LLMClient,
    private contextProvider: ContextProvider
  ) {}

  async continueWriting(
    context: string,
    cursorPosition: number,
    options?: Partial<AIWritingOptions>
  ): Promise<AIWritingResult> {
    const prompt = this.buildContinuePrompt(context, cursorPosition);
    const response = await this.llmClient.generate(prompt, {
      temperature: 0.7,
      maxTokens: 500
    });
    
    return {
      content: response.text,
      suggestions: this.extractSuggestions(response.text),
      confidence: response.confidence
    };
  }

  async polishText(
    text: string,
    options: AIWritingOptions
  ): Promise<AIWritingResult> {
    const prompt = this.buildPolishPrompt(text, options);
    const response = await this.llmClient.generate(prompt);
    
    return {
      content: response.text,
      suggestions: [],
      confidence: response.confidence
    };
  }

  async translateText(
    text: string,
    targetLanguage: string
  ): Promise<AIWritingResult> {
    const prompt = `Translate the following text to ${targetLanguage}:\n\n${text}`;
    const response = await this.llmClient.generate(prompt);
    
    return {
      content: response.text,
      suggestions: [],
      confidence: response.confidence
    };
  }

  private buildContinuePrompt(context: string, cursorPosition: number): string {
    const beforeText = context.slice(0, cursorPosition);
    const afterText = context.slice(cursorPosition);
    
    return `Continue the following text naturally:

Context before cursor:
${beforeText}

Context after cursor:
${afterText}

Please continue from where the cursor is positioned.`;
  }

  private buildPolishPrompt(text: string, options: AIWritingOptions): string {
    return `Polish the following text to make it more ${options.tone || 'professional'}:

${text}

Please provide the polished version.`;
  }

  private extractSuggestions(text: string): string[] {
    // 从 AI 响应中提取建议
    return [];
  }
}
```

### 2.2 智能写作助手组件

```typescript
// components/editor/AIWritingAssistant.tsx
export interface AIWritingAssistantProps {
  editor: Editor;
  documentId: string;
}

export const AIWritingAssistant: React.FC<AIWritingAssistantProps> = ({
  editor,
  documentId
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [mode, setMode] = useState<AIWritingOptions['mode']>('continue');
  const [isGenerating, setIsGenerating] = useState(false);
  const [results, setResults] = useState<AIWritingResult | null>(null);
  
  const aiService = useAIWritingService();
  
  const handleGenerate = async () => {
    const selection = editor.getSelection();
    const context = editor.getText();
    
    setIsGenerating(true);
    try {
      const result = await aiService.continueWriting(
        context,
        selection?.index || context.length,
        { mode }
      );
      setResults(result);
    } finally {
      setIsGenerating(false);
    }
  };
  
  const handleApply = (content: string) => {
    const selection = editor.getSelection();
    editor.insertText(selection?.index || 0, content);
    setIsOpen(false);
  };
  
  return (
    <div className="ai-writing-assistant">
      <Dropdown
        menu={{
          items: [
            { key: 'continue', label: '续写', icon: <EditOutlined /> },
            { key: 'polish', label: '润色', icon: <HighlightOutlined /> },
            { key: 'summary', label: '摘要', icon: <FileTextOutlined /> },
            { key: 'expand', label: '扩写', icon: <ExpandOutlined /> }
          ],
          onClick: ({ key }) => {
            setMode(key as AIWritingOptions['mode']);
            setIsOpen(true);
          }
        }}
      >
        <Button icon={<RobotOutlined />}>AI 助手</Button>
      </Dropdown>
      
      <Modal
        open={isOpen}
        onCancel={() => setIsOpen(false)}
        title="AI 写作助手"
        footer={null}
        width={600}
      >
        <Space direction="vertical" style={{ width: '100%' }}>
          <Radio.Group value={mode} onChange={(e) => setMode(e.target.value)}>
            <Radio.Button value="continue">续写</Radio.Button>
            <Radio.Button value="polish">润色</Radio.Button>
            <Radio.Button value="summary">摘要</Radio.Button>
            <Radio.Button value="expand">扩写</Radio.Button>
          </Radio.Group>
          
          <Button
            type="primary"
            onClick={handleGenerate}
            loading={isGenerating}
            icon={<ThunderboltOutlined />}
          >
            生成内容
          </Button>
          
          {results && (
            <Card>
              <div className="generated-content">{results.content}</div>
              <Space style={{ marginTop: 16 }}>
                <Button onClick={() => handleApply(results.content)}>
                  应用
                </Button>
                <Button onClick={handleGenerate}>重新生成</Button>
              </Space>
            </Card>
          )}
        </Space>
      </Modal>
    </div>
  );
};
```

### 2.3 实时语法检查

```typescript
// services/ai/GrammarChecker.ts
export interface GrammarIssue {
  start: number;
  end: number;
  type: 'grammar' | 'spelling' | 'style' | 'clarity';
  message: string;
  suggestion: string;
  severity: 'low' | 'medium' | 'high';
}

export class GrammarChecker {
  constructor(private llmClient: LLMClient) {}

  async checkText(text: string): Promise<GrammarIssue[]> {
    const prompt = `Check the following text for grammar, spelling, and style issues. Return as JSON array:

${text}

Format: [{"start": 0, "end": 10, "type": "grammar", "message": "...", "suggestion": "...", "severity": "medium"}]`;
    
    const response = await this.llmClient.generate(prompt, {
      temperature: 0.1
    });
    
    try {
      return JSON.parse(response.text);
    } catch {
      return [];
    }
  }

  async checkRealtime(
    text: string,
    onIssuesFound: (issues: GrammarIssue[]) => void
  ): Promise<() => void> {
    // 防抖处理
    const debouncedCheck = debounce(async (text: string) => {
      const issues = await this.checkText(text);
      onIssuesFound(issues);
    }, 1000);
    
    return () => debouncedCheck(text);
  }
}

// components/editor/GrammarHighlighter.tsx
export interface GrammarHighlighterProps {
  editor: Editor;
  issues: GrammarIssue[];
  onFix: (issue: GrammarIssue) => void;
}

export const GrammarHighlighter: React.FC<GrammarHighlighterProps> = ({
  editor,
  issues,
  onFix
}) => {
  return (
    <div className="grammar-highlighter">
      {issues.map((issue, index) => (
        <Popover
          key={index}
          content={
            <div className="grammar-tooltip">
              <div className="grammar-message">{issue.message}</div>
              <div className="grammar-suggestion">
                建议: {issue.suggestion}
              </div>
              <Button size="small" onClick={() => onFix(issue)}>
                修复
              </Button>
            </div>
          }
        >
          <span
            className={`grammar-issue ${issue.type} ${issue.severity}`}
            style={{
              position: 'absolute',
              left: editor.getBounds(issue.start)?.left,
              top: editor.getBounds(issue.start)?.top
            }}
          />
        </Popover>
      ))}
    </div>
  );
};
```

---

## ✅ 三、知识图谱可视化

### 3.1 知识图谱数据模型

```typescript
// models/knowledgeGraph.ts
export interface KnowledgeNode {
  id: string;
  type: 'document' | 'entity' | 'concept' | 'tag' | 'folder';
  label: string;
  properties: Record<string, any>;
  x?: number;
  y?: number;
  size?: number;
  color?: string;
}

export interface KnowledgeEdge {
  id: string;
  source: string;
  target: string;
  type: 'references' | 'contains' | 'relates_to' | 'similar_to' | 'tags';
  label?: string;
  weight: number;
  properties: Record<string, any>;
}

export interface KnowledgeGraph {
  nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
  clusters?: Array<{
    id: string;
    nodes: string[];
    label: string;
    color: string;
  }>;
}

// services/knowledge/KnowledgeGraphService.ts
export class KnowledgeGraphService {
  constructor(
    private documentService: DocumentService,
    private vectorStore: VectorStore,
    private entityExtractor: EntityExtractor
  ) {}

  async buildGraph(documentIds?: string[]): Promise<KnowledgeGraph> {
    const documents = documentIds
      ? await this.documentService.getByIds(documentIds)
      : await this.documentService.getAll();
    
    const nodes: KnowledgeNode[] = [];
    const edges: KnowledgeEdge[] = [];
    
    // 添加文档节点
    for (const doc of documents) {
      nodes.push({
        id: doc.id,
        type: 'document',
        label: doc.title,
        properties: {
          content: doc.content,
          createdAt: doc.createdAt,
          tags: doc.tags
        },
        size: Math.log(doc.content.length + 1) * 5
      });
      
      // 提取实体
      const entities = await this.entityExtractor.extract(doc.content);
      for (const entity of entities) {
        const entityNodeId = `entity:${entity.name}`;
        
        // 添加实体节点（如果不存在）
        if (!nodes.find(n => n.id === entityNodeId)) {
          nodes.push({
            id: entityNodeId,
            type: 'entity',
            label: entity.name,
            properties: { type: entity.type },
            color: this.getEntityColor(entity.type)
          });
        }
        
        // 添加文档-实体边
        edges.push({
          id: `edge:${doc.id}:${entityNodeId}`,
          source: doc.id,
          target: entityNodeId,
          type: 'contains',
          weight: entity.confidence
        });
      }
      
      // 添加标签边
      for (const tag of doc.tags) {
        const tagNodeId = `tag:${tag}`;
        if (!nodes.find(n => n.id === tagNodeId)) {
          nodes.push({
            id: tagNodeId,
            type: 'tag',
            label: tag,
            color: '#722ed1'
          });
        }
        
        edges.push({
          id: `edge:${doc.id}:${tagNodeId}`,
          source: doc.id,
          target: tagNodeId,
          type: 'tags',
          weight: 1
        });
      }
    }
    
    // 添加相似性边
    const similarityEdges = await this.buildSimilarityEdges(documents);
    edges.push(...similarityEdges);
    
    return { nodes, edges };
  }

  private async buildSimilarityEdges(
    documents: Document[]
  ): Promise<KnowledgeEdge[]> {
    const edges: KnowledgeEdge[] = [];
    const threshold = 0.8;
    
    for (let i = 0; i < documents.length; i++) {
      const similar = await this.vectorStore.similaritySearch(
        documents[i].embedding!,
        5,
        { excludeIds: [documents[i].id] }
      );
      
      for (const sim of similar) {
        if (sim.score > threshold) {
          edges.push({
            id: `sim:${documents[i].id}:${sim.documentId}`,
            source: documents[i].id,
            target: sim.documentId,
            type: 'similar_to',
            weight: sim.score
          });
        }
      }
    }
    
    return edges;
  }

  private getEntityColor(type: string): string {
    const colors: Record<string, string> = {
      person: '#ff4d4f',
      organization: '#1890ff',
      location: '#52c41a',
      date: '#faad14',
      concept: '#722ed1'
    };
    return colors[type] || '#8c8c8c';
  }
}
```

### 3.2 知识图谱可视化组件

```typescript
// components/knowledge/KnowledgeGraphView.tsx
export interface KnowledgeGraphViewProps {
  graph: KnowledgeGraph;
  onNodeClick?: (node: KnowledgeNode) => void;
  onEdgeClick?: (edge: KnowledgeEdge) => void;
  width?: number;
  height?: number;
}

export const KnowledgeGraphView: React.FC<KnowledgeGraphViewProps> = ({
  graph,
  onNodeClick,
  onEdgeClick,
  width = 800,
  height = 600
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedNode, setSelectedNode] = useState<KnowledgeNode | null>(null);
  const [layout, setLayout] = useState<'force' | 'circular' | 'hierarchical'>('force');
  
  useEffect(() => {
    if (!containerRef.current) return;
    
    // 使用 D3.js 或 G6 渲染图谱
    const simulation = d3.forceSimulation(graph.nodes as any)
      .force('link', d3.forceLink(graph.edges).id((d: any) => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));
    
    // 渲染节点和边
    renderGraph();
    
    return () => {
      simulation.stop();
    };
  }, [graph, layout]);
  
  const renderGraph = () => {
    // 实现图谱渲染逻辑
  };
  
  return (
    <div className="knowledge-graph-view">
      <div className="graph-toolbar">
        <Radio.Group value={layout} onChange={(e) => setLayout(e.target.value)}>
          <Radio.Button value="force">力导向</Radio.Button>
          <Radio.Button value="circular">环形</Radio.Button>
          <Radio.Button value="hierarchical">层次</Radio.Button>
        </Radio.Group>
        <Button icon={<ZoomInOutlined />} />
        <Button icon={<ZoomOutOutlined />} />
        <Button icon={<FullscreenOutlined />} />
      </div>
      <div ref={containerRef} style={{ width, height }} />
      
      {selectedNode && (
        <KnowledgeNodePanel
          node={selectedNode}
          onClose={() => setSelectedNode(null)}
          relatedNodes={graph.edges
            .filter(e => e.source === selectedNode.id || e.target === selectedNode.id)
            .map(e => {
              const nodeId = e.source === selectedNode.id ? e.target : e.source;
              return graph.nodes.find(n => n.id === nodeId)!;
            })
            .filter(Boolean)
          }
        />
      )}
    </div>
  );
};

// components/knowledge/KnowledgeNodePanel.tsx
export interface KnowledgeNodePanelProps {
  node: KnowledgeNode;
  relatedNodes: KnowledgeNode[];
  onClose: () => void;
}

export const KnowledgeNodePanel: React.FC<KnowledgeNodePanelProps> = ({
  node,
  relatedNodes,
  onClose
}) => {
  return (
    <Drawer
      open={true}
      onClose={onClose}
      title={node.label}
      width={400}
    >
      <Descriptions column={1}>
        <Descriptions.Item label="类型">
          <Tag color={node.color}>{node.type}</Tag>
        </Descriptions.Item>
        {Object.entries(node.properties).map(([key, value]) => (
          <Descriptions.Item key={key} label={key}>
            {typeof value === 'object' ? JSON.stringify(value) : String(value)}
          </Descriptions.Item>
        ))}
      </Descriptions>
      
      <Divider />
      
      <h4>关联节点</h4>
      <List
        dataSource={relatedNodes}
        renderItem={item => (
          <List.Item>
            <Tag color={item.color}>{item.type}</Tag>
            {item.label}
          </List.Item>
        )}
      />
    </Drawer>
  );
};
```

### 3.3 知识导航组件

```typescript
// components/knowledge/KnowledgeNavigator.tsx
export interface KnowledgeNavigatorProps {
  currentDocumentId: string;
  onNavigate: (documentId: string) => void;
}

export const KnowledgeNavigator: React.FC<KnowledgeNavigatorProps> = ({
  currentDocumentId,
  onNavigate
}) => {
  const [relatedDocs, setRelatedDocs] = useState<Document[]>([]);
  const [knowledgePath, setKnowledgePath] = useState<KnowledgeNode[]>([]);
  
  const graphService = useKnowledgeGraphService();
  
  useEffect(() => {
    loadRelatedDocuments();
    loadKnowledgePath();
  }, [currentDocumentId]);
  
  const loadRelatedDocuments = async () => {
    const related = await graphService.getRelatedDocuments(currentDocumentId);
    setRelatedDocs(related);
  };
  
  const loadKnowledgePath = async () => {
    const path = await graphService.getKnowledgePath(currentDocumentId);
    setKnowledgePath(path);
  };
  
  return (
    <div className="knowledge-navigator">
      <Card title="知识导航" size="small">
        <Timeline>
          {knowledgePath.map((node, index) => (
            <Timeline.Item
              key={node.id}
              color={node.type === 'document' ? 'blue' : 'gray'}
            >
              {node.type === 'document' ? (
                <a onClick={() => onNavigate(node.id)}>{node.label}</a>
              ) : (
                node.label
              )}
            </Timeline.Item>
          ))}
        </Timeline>
      </Card>
      
      <Card title="相关文档" size="small" style={{ marginTop: 16 }}>
        <List
          dataSource={relatedDocs}
          renderItem={doc => (
            <List.Item
              actions={[
                <Button
                  type="link"
                  onClick={() => onNavigate(doc.id)}
                >
                  查看
                </Button>
              ]}
            >
              <List.Item.Meta
                title={doc.title}
                description={`相似度: ${(doc.similarity * 100).toFixed(1)}%`}
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};
```

---

## ✅ 四、高级权限管理

### 4.1 权限模型设计

```typescript
// models/permissions.ts
export type PermissionAction = 
  | 'document:read' | 'document:write' | 'document:delete' | 'document:share'
  | 'folder:read' | 'folder:write' | 'folder:delete' | 'folder:share'
  | 'project:read' | 'project:write' | 'project:delete' | 'project:admin'
  | 'comment:read' | 'comment:write' | 'comment:delete'
  | 'analytics:read' | 'settings:read' | 'settings:write';

export interface Permission {
  action: PermissionAction;
  resource: string; // resource type:id pattern
  effect: 'allow' | 'deny';
  conditions?: {
    timeRange?: { start: string; end: string };
    ipRange?: string[];
    mfaRequired?: boolean;
  };
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  inherits?: string[]; // 继承其他角色
  priority: number;
}

export interface AccessPolicy {
  id: string;
  name: string;
  subject: string; // user or group
  resource: string;
  permissions: Permission[];
  createdAt: Date;
  expiresAt?: Date;
}

// services/permissions/PermissionService.ts
export class PermissionService {
  constructor(
    private roleRepository: RoleRepository,
    private policyRepository: PolicyRepository,
    private cache: Cache
  ) {}

  async checkPermission(
    userId: string,
    action: PermissionAction,
    resource: string,
    context?: PermissionContext
  ): Promise<boolean> {
    const cacheKey = `perm:${userId}:${action}:${resource}`;
    const cached = await this.cache.get(cacheKey);
    if (cached !== null) return cached === 'true';
    
    // 获取用户所有权限（包括角色继承）
    const userPermissions = await this.getUserPermissions(userId);
    
    // 检查显式拒绝
    const denied = userPermissions.some(p =>
      p.effect === 'deny' &&
      this.matchPermission(p, action, resource)
    );
    if (denied) {
      await this.cache.set(cacheKey, 'false', 300);
      return false;
    }
    
    // 检查允许
    const allowed = userPermissions.some(p =>
      p.effect === 'allow' &&
      this.matchPermission(p, action, resource) &&
      this.checkConditions(p.conditions, context)
    );
    
    await this.cache.set(cacheKey, allowed ? 'true' : 'false', 300);
    return allowed;
  }

  async getUserPermissions(userId: string): Promise<Permission[]> {
    const user = await this.userRepository.getById(userId);
    const permissions: Permission[] = [];
    
    // 收集角色权限
    for (const roleId of user.roles) {
      const rolePermissions = await this.getRolePermissions(roleId);
      permissions.push(...rolePermissions);
    }
    
    // 收集个人策略权限
    const policies = await this.policyRepository.getBySubject(userId);
    for (const policy of policies) {
      permissions.push(...policy.permissions);
    }
    
    return this.deduplicatePermissions(permissions);
  }

  private async getRolePermissions(roleId: string): Promise<Permission[]> {
    const role = await this.roleRepository.getById(roleId);
    let permissions = [...role.permissions];
    
    // 递归处理继承
    for (const inheritId of role.inherits || []) {
      const inherited = await this.getRolePermissions(inheritId);
      permissions.push(...inherited);
    }
    
    return permissions;
  }

  private matchPermission(
    permission: Permission,
    action: PermissionAction,
    resource: string
  ): boolean {
    const actionMatch = permission.action === action ||
      permission.action === action.split(':')[0] + ':*' ||
      permission.action === '*';
    
    const resourceMatch = this.matchResource(permission.resource, resource);
    
    return actionMatch && resourceMatch;
  }

  private matchResource(pattern: string, resource: string): boolean {
    // 支持通配符匹配
    const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
    return regex.test(resource);
  }

  private checkConditions(
    conditions: Permission['conditions'],
    context?: PermissionContext
  ): boolean {
    if (!conditions) return true;
    
    if (conditions.timeRange) {
      const now = new Date();
      const start = new Date(conditions.timeRange.start);
      const end = new Date(conditions.timeRange.end);
      if (now < start || now > end) return false;
    }
    
    if (conditions.ipRange && context?.ip) {
      if (!conditions.ipRange.includes(context.ip)) return false;
    }
    
    if (conditions.mfaRequired && !context?.mfaVerified) {
      return false;
    }
    
    return true;
  }
}
```

### 4.2 权限管理界面

```typescript
// components/permissions/RoleManager.tsx
export interface RoleManagerProps {
  projectId: string;
}

export const RoleManager: React.FC<RoleManagerProps> = ({ projectId }) => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const permissionService = usePermissionService();
  
  useEffect(() => {
    loadRoles();
  }, [projectId]);
  
  const loadRoles = async () => {
    const data = await permissionService.getProjectRoles(projectId);
    setRoles(data);
  };
  
  const handleSaveRole = async (role: Partial<Role>) => {
    if (selectedRole) {
      await permissionService.updateRole(selectedRole.id, role);
    } else {
      await permissionService.createRole({ ...role, projectId } as Role);
    }
    loadRoles();
    setIsModalOpen(false);
  };
  
  return (
    <div className="role-manager">
      <div className="role-header">
        <h3>角色管理</h3>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setSelectedRole(null);
            setIsModalOpen(true);
          }}
        >
          新建角色
        </Button>
      </div>
      
      <Table
        dataSource={roles}
        columns={[
          { title: '角色名称', dataIndex: 'name' },
          { title: '描述', dataIndex: 'description' },
          { title: '权限数', render: (_, r) => r.permissions.length },
          {
            title: '操作',
            render: (_, role) => (
              <Space>
                <Button
                  icon={<EditOutlined />}
                  onClick={() => {
                    setSelectedRole(role);
                    setIsModalOpen(true);
                  }}
                />
                <Popconfirm
                  title="确认删除?"
                  onConfirm={() => handleDeleteRole(role.id)}
                >
                  <Button icon={<DeleteOutlined />} danger />
                </Popconfirm>
              </Space>
            )
          }
        ]}
      />
      
      <RoleEditModal
        open={isModalOpen}
        role={selectedRole}
        onCancel={() => setIsModalOpen(false)}
        onSave={handleSaveRole}
      />
    </div>
  );
};

// components/permissions/PermissionEditor.tsx
export interface PermissionEditorProps {
  permissions: Permission[];
  onChange: (permissions: Permission[]) => void;
}

export const PermissionEditor: React.FC<PermissionEditorProps> = ({
  permissions,
  onChange
}) => {
  const [selectedResource, setSelectedResource] = useState<string>('');
  
  const resourceTypes = [
    { value: 'document', label: '文档' },
    { value: 'folder', label: '文件夹' },
    { value: 'project', label: '项目' },
    { value: 'comment', label: '评论' }
  ];
  
  const actions = [
    { value: 'read', label: '读取' },
    { value: 'write', label: '写入' },
    { value: 'delete', label: '删除' },
    { value: 'share', label: '分享' }
  ];
  
  const addPermission = (resourceType: string, action: string) => {
    const newPermission: Permission = {
      action: `${resourceType}:${action}` as PermissionAction,
      resource: `${resourceType}:*`,
      effect: 'allow'
    };
    onChange([...permissions, newPermission]);
  };
  
  return (
    <div className="permission-editor">
      <div className="permission-grid">
        {resourceTypes.map(type => (
          <Card key={type.value} title={type.label} size="small">
            <Checkbox.Group
              value={permissions
                .filter(p => p.action.startsWith(type.value))
                .map(p => p.action.split(':')[1])
              }
              onChange={(checked) => {
                // 更新权限
              }}
            >
              {actions.map(action => (
                <Checkbox key={action.value} value={action.value}>
                  {action.label}
                </Checkbox>
              ))}
            </Checkbox.Group>
          </Card>
        ))}
      </div>
      
      <div className="permission-advanced">
        <h4>高级条件</h4>
        <Form layout="vertical">
          <Form.Item label="时间限制">
            <TimePicker.RangePicker />
          </Form.Item>
          <Form.Item label="IP 限制">
            <Select mode="tags" placeholder="输入允许 IP" />
          </Form.Item>
          <Form.Item label="需要 MFA">
            <Switch />
          </Form.Item>
        </Form>
      </div>
    </div>
  );
};
```

---

## ✅ 五、数据备份与恢复

### 5.1 备份服务架构

```typescript
// services/backup/BackupService.ts
export interface BackupConfig {
  schedule: 'daily' | 'weekly' | 'monthly';
  time: string; // HH:mm
  retentionDays: number;
  destinations: BackupDestination[];
  includeAttachments: boolean;
  compressionLevel: 'none' | 'fast' | 'best';
  encryptionEnabled: boolean;
}

export interface BackupDestination {
  type: 'local' | 's3' | 'gcs' | 'azure';
  config: Record<string, string>;
}

export interface BackupJob {
  id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  type: 'full' | 'incremental';
  startedAt: Date;
  completedAt?: Date;
  size: number;
  fileCount: number;
  error?: string;
}

export interface RestorePoint {
  id: string;
  createdAt: Date;
  type: 'full' | 'incremental';
  size: number;
  metadata: {
    documentCount: number;
    userCount: number;
    version: string;
  };
}

export class BackupService {
  constructor(
    private db: Database,
    private fileStorage: FileStorage,
    private scheduler: Scheduler,
    private encryption: EncryptionService
  ) {}

  async createBackup(type: 'full' | 'incremental' = 'full'): Promise<BackupJob> {
    const job: BackupJob = {
      id: generateUUID(),
      status: 'running',
      type,
      startedAt: new Date(),
      size: 0,
      fileCount: 0
    };
    
    try {
      // 创建备份目录
      const backupDir = `backups/${job.id}`;
      await this.fileStorage.createDirectory(backupDir);
      
      // 备份数据库
      const dbBackup = await this.backupDatabase(type);
      await this.fileStorage.writeFile(
        `${backupDir}/database.sql`,
        dbBackup
      );
      
      // 备份文档内容
      const documents = await this.db.documents.findAll();
      for (const doc of documents) {
        if (type === 'incremental' && doc.updatedAt < job.startedAt) {
          continue;
        }
        
        const docData = JSON.stringify(doc);
        await this.fileStorage.writeFile(
          `${backupDir}/documents/${doc.id}.json`,
          docData
        );
        job.fileCount++;
      }
      
      // 备份附件
      if (this.config.includeAttachments) {
        const attachments = await this.fileStorage.list('attachments/');
        for (const file of attachments) {
          const content = await this.fileStorage.readFile(file);
          await this.fileStorage.writeFile(
            `${backupDir}/attachments/${path.basename(file)}`,
            content
          );
        }
      }
      
      // 压缩备份
      const compressedSize = await this.compressBackup(backupDir);
      job.size = compressedSize;
      
      // 加密（如果启用）
      if (this.config.encryptionEnabled) {
        await this.encryptBackup(`${backupDir}.zip`);
      }
      
      // 上传到远程存储
      for (const dest of this.config.destinations) {
        await this.uploadToDestination(`${backupDir}.zip.enc`, dest);
      }
      
      job.status = 'completed';
      job.completedAt = new Date();
      
      // 清理旧备份
      await this.cleanupOldBackups();
      
    } catch (error) {
      job.status = 'failed';
      job.error = error.message;
    }
    
    await this.saveBackupJob(job);
    return job;
  }

  async restoreFromBackup(restorePointId: string): Promise<void> {
    // 验证备份完整性
    const backup = await this.getBackup(restorePointId);
    if (!backup) throw new Error('Backup not found');
    
    // 创建恢复任务
    const restoreJob = await this.createRestoreJob(backup);
    
    try {
      // 下载备份文件
      const backupPath = await this.downloadBackup(backup);
      
      // 解密
      if (this.config.encryptionEnabled) {
        await this.decryptBackup(backupPath);
      }
      
      // 解压
      const extractPath = await this.extractBackup(backupPath);
      
      // 恢复数据库
      const dbBackup = await this.fileStorage.readFile(
        `${extractPath}/database.sql`
      );
      await this.restoreDatabase(dbBackup);
      
      // 恢复文档
      const docFiles = await this.fileStorage.list(`${extractPath}/documents/`);
      for (const file of docFiles) {
        const content = await this.fileStorage.readFile(file);
        const doc = JSON.parse(content);
        await this.db.documents.upsert(doc);
      }
      
      // 恢复附件
      const attachmentFiles = await this.fileStorage.list(
        `${extractPath}/attachments/`
      );
      for (const file of attachmentFiles) {
        const content = await this.fileStorage.readFile(file);
        await this.fileStorage.writeFile(
          `attachments/${path.basename(file)}`,
          content
        );
      }
      
      restoreJob.status = 'completed';
      
    } catch (error) {
      restoreJob.status = 'failed';
      restoreJob.error = error.message;
      throw error;
    }
  }

  private async backupDatabase(type: 'full' | 'incremental'): Promise<Buffer> {
    // 使用 pg_dump 或相应工具
    const command = type === 'full'
      ? `pg_dump -h ${this.db.host} -U ${this.db.user} ${this.db.name}`
      : `pg_dump -h ${this.db.host} -U ${this.db.user} --data-only ${this.db.name}`;
    
    return exec(command);
  }

  private async compressBackup(backupDir: string): Promise<number> {
    const output = `${backupDir}.zip`;
    const level = this.config.compressionLevel === 'best' ? 9 :
      this.config.compressionLevel === 'fast' ? 1 : 6;
    
    await exec(`zip -${level} -r ${output} ${backupDir}`);
    
    const stats = await this.fileStorage.stat(output);
    return stats.size;
  }

  private async cleanupOldBackups(): Promise<void> {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - this.config.retentionDays);
    
    const oldBackups = await this.getBackupsBefore(cutoffDate);
    for (const backup of oldBackups) {
      await this.fileStorage.delete(`backups/${backup.id}*`);
      for (const dest of this.config.destinations) {
        await this.deleteFromDestination(backup.id, dest);
      }
    }
  }
}
```

### 5.2 备份管理界面

```typescript
// components/backup/BackupManager.tsx
export const BackupManager: React.FC = () => {
  const [backups, setBackups] = useState<BackupJob[]>([]);
  const [config, setConfig] = useState<BackupConfig | null>(null);
  const [isRestoring, setIsRestoring] = useState(false);
  
  const backupService = useBackupService();
  
  useEffect(() => {
    loadBackups();
    loadConfig();
  }, []);
  
  const loadBackups = async () => {
    const data = await backupService.listBackups();
    setBackups(data);
  };
  
  const loadConfig = async () => {
    const data = await backupService.getConfig();
    setConfig(data);
  };
  
  const handleCreateBackup = async (type: 'full' | 'incremental') => {
    await backupService.createBackup(type);
    loadBackups();
  };
  
  const handleRestore = async (backupId: string) => {
    Modal.confirm({
      title: '确认恢复',
      content: '恢复操作将覆盖当前数据，是否继续？',
      onOk: async () => {
        setIsRestoring(true);
        try {
          await backupService.restoreFromBackup(backupId);
          message.success('恢复成功');
        } finally {
          setIsRestoring(false);
        }
      }
    });
  };
  
  return (
    <div className="backup-manager">
      <Card title="备份管理">
        <div className="backup-actions">
          <Space>
            <Button
              type="primary"
              icon={<CloudUploadOutlined />}
              onClick={() => handleCreateBackup('full')}
            >
              完整备份
            </Button>
            <Button
              icon={<CloudUploadOutlined />}
              onClick={() => handleCreateBackup('incremental')}
            >
              增量备份
            </Button>
            <Button
              icon={<SettingOutlined />}
              onClick={() => setConfigModalOpen(true)}
            >
              备份设置
            </Button>
          </Space>
        </div>
        
        <Table
          dataSource={backups}
          columns={[
            {
              title: '类型',
              dataIndex: 'type',
              render: (type) => (
                <Tag color={type === 'full' ? 'blue' : 'green'}>
                  {type === 'full' ? '完整' : '增量'}
                </Tag>
              )
            },
            {
              title: '状态',
              dataIndex: 'status',
              render: (status) => {
                const statusMap = {
                  pending: { color: 'default', text: '等待中' },
                  running: { color: 'processing', text: '进行中' },
                  completed: { color: 'success', text: '完成' },
                  failed: { color: 'error', text: '失败' }
                };
                return <Tag {...statusMap[status]} />;
              }
            },
            {
              title: '大小',
              dataIndex: 'size',
              render: (size) => formatFileSize(size)
            },
            {
              title: '文件数',
              dataIndex: 'fileCount'
            },
            {
              title: '创建时间',
              dataIndex: 'startedAt',
              render: (date) => formatDate(date)
            },
            {
              title: '操作',
              render: (_, backup) => (
                <Space>
                  {backup.status === 'completed' && (
                    <Button
                      onClick={() => handleRestore(backup.id)}
                      loading={isRestoring}
                    >
                      恢复
                    </Button>
                  )}
                  <Button
                    icon={<DownloadOutlined />}
                    onClick={() => handleDownload(backup.id)}
                  >
                    下载
                  </Button>
                  <Popconfirm
                    title="确认删除?"
                    onConfirm={() => handleDelete(backup.id)}
                  >
                    <Button icon={<DeleteOutlined />} danger />
                  </Popconfirm>
                </Space>
              )
            }
          ]}
        />
      </Card>
      
      <BackupConfigModal
        config={config}
        open={configModalOpen}
        onCancel={() => setConfigModalOpen(false)}
        onSave={handleSaveConfig}
      />
    </div>
  );
};
```

---

## 📊 版本总结

### v3.0.13 交付清单

| 功能模块 | 状态 | 关键文件 |
|----------|------|----------|
| 移动端适配 | 📝 设计完成 | hooks/useBreakpoint.ts, components/mobile/ |
| AI 辅助写作 | 📝 设计完成 | services/ai/AIWritingService.ts, components/editor/ |
| 知识图谱可视化 | 📝 设计完成 | services/knowledge/, components/knowledge/ |
| 高级权限管理 | 📝 设计完成 | services/permissions/, components/permissions/ |
| 数据备份与恢复 | 📝 设计完成 | services/backup/, components/backup/ |

### 下一步计划 (v3.0.14)

- [ ] 智能推荐系统
- [ ] 文档版本对比
- [ ] 自动化工作流
- [ ] 高级分析报告
- [ ] 多语言支持完善

---

**更新时间**: 2026-03-30 23:00
