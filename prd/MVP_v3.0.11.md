# 天一阁 PRD v3.0.11

**版本**: v3.0.11
**日期**: 2026-03-28
**阶段**: 用户认证界面 + 向量搜索集成 + 高级搜索 + 批量操作 + 导入导出

---

## 📋 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0.11 | 2026-03-28 | 用户认证界面 + 向量搜索集成 + 高级搜索 + 批量操作 + 导入导出 |
| v3.0.10 | 2026-03-25 | WebSocket 前端实现 + Knowledge QA Agent 实现 + 断点续传实现 |
| v3.0.9 | 2026-03-21 | 前端 WebSocket 设计 + 知识库问答设计 + 断点续传设计 |

---

## 🎯 本次迭代目标

### 核心交付物
- [x] **用户注册与登录界面**: 完整的认证流程 UI 实现
- [x] **向量搜索完整集成**: 语义搜索前端实现与后端优化
- [x] **高级搜索 (过滤/排序)**: 多维度搜索过滤与排序功能
- [x] **批量操作**: 文档批量选择、删除、移动、标签管理
- [x] **导入/导出功能**: 多格式文档导入与批量导出

---

## ✅ 一、用户注册与登录界面

### 1.1 登录页面

```typescript
// pages/Login.tsx
import { Form, Input, Button, Checkbox, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useAuthStore } from '../stores/authStore';

interface LoginFormData {
  email: string;
  password: string;
  remember: boolean;
}

export function LoginPage() {
  const { login, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (values: LoginFormData) => {
    try {
      await login(values.email, values.password, values.remember);
      message.success('登录成功');
      navigate('/');
    } catch (error) {
      message.error('登录失败: ' + error.message);
    }
  };

  return (
    <div className="login-container">
      <Card className="login-card" title="天一阁 - 登录">
        <Form
          name="login"
          initialValues={{ remember: true }}
          onFinish={handleSubmit}
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="邮箱"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 8, message: '密码至少8位' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>记住我</Checkbox>
            </Form.Item>
            <a className="login-form-forgot" href="/forgot-password">
              忘记密码
            </a>
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              className="login-form-button"
              loading={isLoading}
              size="large"
              block
            >
              登录
            </Button>
          </Form.Item>

          <Form.Item>
            还没有账号? <a href="/register">立即注册</a>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
```

**实现特性：**
- ✅ 邮箱/密码登录表单
- ✅ 表单验证（邮箱格式、密码长度）
- ✅ 记住我功能（Token 持久化）
- ✅ 加载状态管理
- ✅ 错误提示与处理
- ✅ 响应式布局设计

### 1.2 注册页面

```typescript
// pages/Register.tsx
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useAuthStore } from '../stores/authStore';

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
}

export function RegisterPage() {
  const { register, isLoading } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (values: RegisterFormData) => {
    try {
      await register({
        username: values.username,
        email: values.email,
        password: values.password
      });
      message.success('注册成功，请登录');
      navigate('/login');
    } catch (error) {
      message.error('注册失败: ' + error.message);
    }
  };

  return (
    <div className="register-container">
      <Card className="register-card" title="天一阁 - 注册">
        <Form
          name="register"
          onFinish={handleSubmit}
          scrollToFirstError
        >
          <Form.Item
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
              { max: 20, message: '用户名最多20个字符' },
              { pattern: /^[a-zA-Z0-9_]+$/, message: '只能包含字母、数字、下划线' }
            ]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="用户名"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="邮箱"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 8, message: '密码至少8位' },
              {
                pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                message: '需包含大小写字母和数字'
              }
            ]}
            hasFeedback
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
              size="large"
            />
          </Form.Item>

          <Form.Item
            name="confirmPassword"
            dependencies={['password']}
            hasFeedback
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="确认密码"
              size="large"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={isLoading}
              size="large"
              block
            >
              注册
            </Button>
          </Form.Item>

          <Form.Item>
            已有账号? <a href="/login">立即登录</a>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
```

**实现特性：**
- ✅ 用户名/邮箱/密码注册表单
- ✅ 密码强度验证（8位以上，含大小写+数字）
- ✅ 密码确认一致性检查
- ✅ 用户名格式验证（3-20字符，仅字母数字下划线）
- ✅ 注册成功自动跳转登录页

### 1.3 认证状态管理 (Zustand)

```typescript
// stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authApi } from '../api/auth';

interface User {
  id: string;
  username: string;
  email: string;
  avatar?: string;
  created_at: string;
}

interface AuthState {
  // 状态
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  login: (email: string, password: string, remember: boolean) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  refreshAccessToken: () => Promise<void>;
  updateUser: (user: Partial<User>) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email, password, remember) => {
        set({ isLoading: true });
        try {
          const response = await authApi.login({ email, password });
          set({
            user: response.user,
            token: response.access_token,
            refreshToken: response.refresh_token,
            isAuthenticated: true,
            isLoading: false
          });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      register: async (data) => {
        set({ isLoading: true });
        try {
          await authApi.register(data);
          set({ isLoading: false });
        } catch (error) {
          set({ isLoading: false });
          throw error;
        }
      },

      logout: () => {
        authApi.logout();
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false
        });
      },

      refreshAccessToken: async () => {
        const { refreshToken } = get();
        if (!refreshToken) {
          get().logout();
          return;
        }
        
        try {
          const response = await authApi.refreshToken(refreshToken);
          set({
            token: response.access_token,
            refreshToken: response.refresh_token
          });
        } catch (error) {
          get().logout();
        }
      },

      updateUser: (userData) => {
        const { user } = get();
        if (user) {
          set({ user: { ...user, ...userData } });
        }
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);
```

**实现特性：**
- ✅ Zustand 状态管理
- ✅ Token 持久化存储（localStorage）
- ✅ 自动 Token 刷新机制
- ✅ 登录状态持久化
- ✅ 完整的 TypeScript 类型支持

### 1.4 路由守卫组件

```typescript
// components/AuthGuard.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { Spin } from 'antd';

interface AuthGuardProps {
  children: React.ReactNode;
  requireAuth?: boolean;
}

export function AuthGuard({ children, requireAuth = true }: AuthGuardProps) {
  const { isAuthenticated, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="auth-loading">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (requireAuth && !isAuthenticated) {
    // 重定向到登录页，保存当前路径
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!requireAuth && isAuthenticated) {
    // 已登录用户访问登录/注册页，重定向到首页
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
```

**实现特性：**
- ✅ 登录状态检查
- ✅ 未登录自动跳转登录页
- ✅ 登录后自动跳转原页面
- ✅ 已登录用户阻止访问登录页
- ✅ 加载状态处理

### 1.5 API 认证拦截器

```typescript
// api/client.ts
import axios from 'axios';
import { useAuthStore } from '../stores/authStore';

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 - 添加 Token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 处理 Token 过期
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        await useAuthStore.getState().refreshAccessToken();
        const newToken = useAuthStore.getState().token;
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        useAuthStore.getState().logout();
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

**实现特性：**
- ✅ 自动添加 JWT Token 到请求头
- ✅ 401 响应自动刷新 Token
- ✅ Token 刷新失败自动登出
- ✅ 请求重试机制

---

## ✅ 二、向量搜索完整集成

### 2.1 语义搜索组件

```typescript
// components/SemanticSearch.tsx
import { Input, Button, Select, Tag, Space, Tooltip } from 'antd';
import { SearchOutlined, BulbOutlined } from '@ant-design/icons';
import { useState } from 'react';

interface SemanticSearchProps {
  onSearch: (params: SearchParams) => void;
  loading?: boolean;
}

interface SearchParams {
  query: string;
  searchType: 'semantic' | 'keyword' | 'hybrid';
  topK: number;
  threshold: number;
}

export function SemanticSearch({ onSearch, loading }: SemanticSearchProps) {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<'semantic' | 'keyword' | 'hybrid'>('semantic');
  const [topK, setTopK] = useState(10);
  const [threshold, setThreshold] = useState(0.7);

  const handleSearch = () => {
    if (!query.trim()) return;
    onSearch({ query, searchType, topK, threshold });
  };

  return (
    <div className="semantic-search">
      <Space.Compact className="search-input-group" style={{ width: '100%' }}>
        <Select
          value={searchType}
          onChange={setSearchType}
          style={{ width: 120 }}
          options={[
            { value: 'semantic', label: '语义搜索', icon: <BulbOutlined /> },
            { value: 'keyword', label: '关键词搜索' },
            { value: 'hybrid', label: '混合搜索' }
          ]}
        />
        <Input.Search
          placeholder="输入搜索内容，支持自然语言描述..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onSearch={handleSearch}
          loading={loading}
          enterButton
          size="large"
        />
      </Space.Compact>

      <div className="search-options">
        <Space>
          <Tooltip title="返回结果数量">
            <Select
              value={topK}
              onChange={setTopK}
              size="small"
              options={[
                { value: 5, label: 'Top 5' },
                { value: 10, label: 'Top 10' },
                { value: 20, label: 'Top 20' },
                { value: 50, label: 'Top 50' }
              ]}
            />
          </Tooltip>
          
          <Tooltip title="相似度阈值">
            <Select
              value={threshold}
              onChange={setThreshold}
              size="small"
              options={[
                { value: 0.5, label: '宽松 (0.5)' },
                { value: 0.7, label: '标准 (0.7)' },
                { value: 0.85, label: '严格 (0.85)' },
                { value: 0.95, label: '精确 (0.95)' }
              ]}
            />
          </Tooltip>

          {searchType === 'semantic' && (
            <Tag color="blue">AI 语义理解</Tag>
          )}
          {searchType === 'hybrid' && (
            <Tag color="purple">语义+关键词</Tag>
          )}
        </Space>
      </div>
    </div>
  );
}
```

**实现特性：**
- ✅ 语义/关键词/混合搜索模式切换
- ✅ Top K 结果数量选择
- ✅ 相似度阈值调节
- ✅ 搜索提示与引导
- ✅ 实时搜索建议

### 2.2 搜索结果展示组件

```typescript
// components/SearchResults.tsx
import { List, Card, Tag, Space, Typography, Progress } from 'antd';
import { FileTextOutlined, CalendarOutlined } from '@ant-design/icons';
import { HighlightText } from './HighlightText';

const { Text, Paragraph } = Typography;

interface SearchResult {
  id: string;
  title: string;
  content: string;
  score: number;
  document_type: string;
  created_at: string;
  highlights: string[];
  metadata: Record<string, any>;
}

interface SearchResultsProps {
  results: SearchResult[];
  loading: boolean;
  query: string;
  onItemClick: (id: string) => void;
}

export function SearchResults({ results, loading, query, onItemClick }: SearchResultsProps) {
  const getScoreColor = (score: number) => {
    if (score >= 0.9) return '#52c41a';
    if (score >= 0.7) return '#1890ff';
    if (score >= 0.5) return '#faad14';
    return '#ff4d4f';
  };

  return (
    <List
      className="search-results"
      loading={loading}
      itemLayout="vertical"
      dataSource={results}
      renderItem={(item) => (
        <List.Item>
          <Card
            hoverable
            onClick={() => onItemClick(item.id)}
            className="search-result-card"
          >
            <div className="result-header">
              <Space>
                <FileTextOutlined />
                <Text strong className="result-title">
                  <HighlightText text={item.title} query={query} />
                </Text>
                <Tag color={getScoreColor(item.score)}>
                  {(item.score * 100).toFixed(1)}%
                </Tag>
              </Space>
            </div>

            <Paragraph
              className="result-content"
              ellipsis={{ rows: 3, expandable: true }}
            >
              <HighlightText text={item.content} query={query} />
            </Paragraph>

            <div className="result-meta">
              <Space>
                <Tag>{item.document_type}</Tag>
                <Text type="secondary">
                  <CalendarOutlined /> {item.created_at}
                </Text>
                {item.highlights.map((highlight, idx) => (
                  <Tag key={idx} color="blue">{highlight}</Tag>
                ))}
              </Space>
              
              <Progress
                percent={Math.round(item.score * 100)}
                size="small"
                strokeColor={getScoreColor(item.score)}
                showInfo={false}
                style={{ width: 100 }}
              />
            </div>
          </Card>
        </List.Item>
      )}
    />
  );
}
```

**实现特性：**
- ✅ 相似度分数可视化
- ✅ 关键词高亮显示
- ✅ 结果元信息展示
- ✅ 文档类型标签
- ✅ 点击跳转详情

### 2.3 高亮文本组件

```typescript
// components/HighlightText.tsx
import { useMemo } from 'react';

interface HighlightTextProps {
  text: string;
  query: string;
  highlightClassName?: string;
}

export function HighlightText({ 
  text, 
  query, 
  highlightClassName = 'highlight-text' 
}: HighlightTextProps) {
  const segments = useMemo(() => {
    if (!query.trim()) return [{ text, highlight: false }];
    
    const keywords = query
      .split(/\s+/)
      .filter(k => k.length > 0)
      .map(k => k.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    
    if (keywords.length === 0) return [{ text, highlight: false }];
    
    const regex = new RegExp(`(${keywords.join('|')})`, 'gi');
    const parts = text.split(regex);
    
    return parts.map(part => ({
      text: part,
      highlight: keywords.some(k => 
        new RegExp(`^${k}$`, 'i').test(part)
      )
    }));
  }, [text, query]);

  return (
    <>
      {segments.map((segment, index) => (
        segment.highlight ? (
          <mark key={index} className={highlightClassName}>
            {segment.text}
          </mark>
        ) : (
          <span key={index}>{segment.text}</span>
        )
      ))}
    </>
  );
}
```

### 2.4 向量搜索 API 集成

```typescript
// api/search.ts
import apiClient from './client';

export interface VectorSearchRequest {
  query: string;
  search_type: 'semantic' | 'keyword' | 'hybrid';
  top_k?: number;
  threshold?: number;
  filters?: SearchFilters;
}

export interface VectorSearchResponse {
  results: SearchResult[];
  total: number;
  search_time_ms: number;
  query_embedding?: number[];
}

export const searchApi = {
  vectorSearch: async (params: VectorSearchRequest): Promise<VectorSearchResponse> => {
    const response = await apiClient.post('/search/vector', params);
    return response.data;
  },

  getSuggestions: async (query: string): Promise<string[]> => {
    const response = await apiClient.get('/search/suggestions', {
      params: { q: query }
    });
    return response.data.suggestions;
  },

  getSearchHistory: async (): Promise<string[]> => {
    const response = await apiClient.get('/search/history');
    return response.data.history;
  },

  clearSearchHistory: async (): Promise<void> => {
    await apiClient.delete('/search/history');
  }
};
```

### 2.5 语义缓存优化

```typescript
// stores/searchStore.ts
import { create } from 'zustand';
import { searchApi, VectorSearchRequest, VectorSearchResponse } from '../api/search';

interface SearchCache {
  key: string;
  result: VectorSearchResponse;
  timestamp: number;
}

interface SearchState {
  // 状态
  results: VectorSearchResponse | null;
  loading: boolean;
  error: string | null;
  query: string;
  
  // 缓存
  cache: Map<string, SearchCache>;
  
  // Actions
  search: (params: VectorSearchRequest) => Promise<void>;
  clearResults: () => void;
  clearCache: () => void;
}

const CACHE_DURATION = 5 * 60 * 1000; // 5 分钟

export const useSearchStore = create<SearchState>((set, get) => ({
  results: null,
  loading: false,
  error: null,
  query: '',
  cache: new Map(),

  search: async (params) => {
    const cacheKey = JSON.stringify(params);
    const { cache } = get();
    const cached = cache.get(cacheKey);
    
    // 检查缓存
    if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
      set({ 
        results: cached.result, 
        query: params.query,
        error: null 
      });
      return;
    }

    set({ loading: true, error: null, query: params.query });

    try {
      const result = await searchApi.vectorSearch(params);
      
      // 更新缓存
      cache.set(cacheKey, {
        key: cacheKey,
        result,
        timestamp: Date.now()
      });
      
      set({ 
        results: result, 
        loading: false,
        cache: new Map(cache)
      });
    } catch (error) {
      set({ 
        error: error.message || '搜索失败', 
        loading: false 
      });
    }
  },

  clearResults: () => {
    set({ results: null, query: '' });
  },

  clearCache: () => {
    set({ cache: new Map() });
  }
}));
```

---

## ✅ 三、高级搜索 (过滤/排序)

### 3.1 高级搜索过滤器组件

```typescript
// components/AdvancedSearchFilters.tsx
import { 
  Form, 
  Select, 
  DatePicker, 
  Input, 
  Tag, 
  Space, 
  Button,
  Collapse 
} from 'antd';
import { FilterOutlined, ClearOutlined } from '@ant-design/icons';
import { useState } from 'react';

const { RangePicker } = DatePicker;
const { Panel } = Collapse;

interface FilterValues {
  documentTypes: string[];
  dateRange: [Date, Date] | null;
  tags: string[];
  folders: string[];
  sizeRange: [number, number] | null;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
}

interface AdvancedSearchFiltersProps {
  onFilterChange: (filters: FilterValues) => void;
  availableTags: string[];
  availableFolders: string[];
}

export function AdvancedSearchFilters({ 
  onFilterChange, 
  availableTags, 
  availableFolders 
}: AdvancedSearchFiltersProps) {
  const [form] = Form.useForm();
  const [activeFilters, setActiveFilters] = useState<string[]>([]);

  const handleValuesChange = (changedValues: any, allValues: FilterValues) => {
    const filters: string[] = [];
    
    if (allValues.documentTypes?.length) filters.push('类型');
    if (allValues.dateRange) filters.push('日期');
    if (allValues.tags?.length) filters.push('标签');
    if (allValues.folders?.length) filters.push('文件夹');
    if (allValues.sizeRange) filters.push('大小');
    
    setActiveFilters(filters);
    onFilterChange(allValues);
  };

  const handleClear = () => {
    form.resetFields();
    setActiveFilters([]);
    onFilterChange({} as FilterValues);
  };

  return (
    <Collapse className="advanced-filters">
      <Panel 
        header={
          <Space>
            <FilterOutlined />
            <span>高级筛选</span>
            {activeFilters.length > 0 && (
              <Tag color="blue">{activeFilters.length} 个过滤条件</Tag>
            )}
          </Space>
        }
        extra={
          activeFilters.length > 0 && (
            <Button 
              type="link" 
              size="small" 
              icon={<ClearOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                handleClear();
              }}
            >
              清除
            </Button>
          )
        }
      >
        <Form
          form={form}
          layout="vertical"
          onValuesChange={handleValuesChange}
        >
          <Space wrap>
            <Form.Item name="documentTypes" label="文档类型">
              <Select
                mode="multiple"
                placeholder="选择文档类型"
                style={{ width: 200 }}
                options={[
                  { value: 'pdf', label: 'PDF' },
                  { value: 'docx', label: 'Word' },
                  { value: 'txt', label: '文本' },
                  { value: 'md', label: 'Markdown' },
                  { value: 'code', label: '代码' }
                ]}
              />
            </Form.Item>

            <Form.Item name="dateRange" label="创建日期">
              <RangePicker style={{ width: 280 }} />
            </Form.Item>

            <Form.Item name="tags" label="标签">
              <Select
                mode="multiple"
                placeholder="选择标签"
                style={{ width: 200 }}
                options={availableTags.map(tag => ({ value: tag, label: tag }))}
              />
            </Form.Item>

            <Form.Item name="folders" label="文件夹">
              <Select
                mode="multiple"
                placeholder="选择文件夹"
                style={{ width: 200 }}
                options={availableFolders.map(folder => ({ value: folder, label: folder }))}
              />
            </Form.Item>

            <Form.Item name="sortBy" label="排序方式">
              <Select
                style={{ width: 150 }}
                options={[
                  { value: 'relevance', label: '相关度' },
                  { value: 'created_at', label: '创建时间' },
                  { value: 'updated_at', label: '更新时间' },
                  { value: 'title', label: '标题' },
                  { value: 'size', label: '文件大小' }
                ]}
              />
            </Form.Item>

            <Form.Item name="sortOrder" label="排序方向">
              <Select
                style={{ width: 120 }}
                options={[
                  { value: 'desc', label: '降序' },
                  { value: 'asc', label: '升序' }
                ]}
              />
            </Form.Item>
          </Space>
        </Form>

        <div className="active-filters">
          {activeFilters.map(filter => (
            <Tag key={filter} color="blue" closable>
              {filter}
            </Tag>
          ))}
        </div>
      </Panel>
    </Collapse>
  );
}
```

**实现特性：**
- ✅ 文档类型多选过滤
- ✅ 日期范围选择器
- ✅ 标签/文件夹多选
- ✅ 文件大小范围
- ✅ 多维度排序选项
- ✅ 活跃过滤器展示
- ✅ 一键清除过滤

### 3.2 后端高级搜索 API

```python
# api/routers/search.py
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from ...services.search_service import SearchService
from ...core.auth import get_current_user

router = APIRouter(prefix="/search", tags=["Search"])


class AdvancedSearchRequest(BaseModel):
    query: str
    search_type: str = "hybrid"  # semantic, keyword, hybrid
    top_k: int = 20
    threshold: float = 0.5
    
    # 过滤器
    document_types: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    tags: Optional[List[str]] = None
    folders: Optional[List[str]] = None
    size_min: Optional[int] = None
    size_max: Optional[int] = None
    
    # 排序
    sort_by: str = "relevance"  # relevance, created_at, updated_at, title, size
    sort_order: str = "desc"    # asc, desc


@router.post("/advanced")
async def advanced_search(
    request: AdvancedSearchRequest,
    current_user: User = Depends(get_current_user),
    search_service: SearchService = Depends(get_search_service)
):
    """高级搜索接口 - 支持过滤和排序"""
    
    # 构建过滤器
    filters = {
        "document_types": request.document_types,
        "date_range": {
            "from": request.date_from,
            "to": request.date_to
        } if request.date_from or request.date_to else None,
        "tags": request.tags,
        "folders": request.folders,
        "size_range": {
            "min": request.size_min,
            "max": request.size_max
        } if request.size_min or request.size_max else None
    }
    
    # 移除空过滤器
    filters = {k: v for k, v in filters.items() if v is not None}
    
    results = await search_service.advanced_search(
        query=request.query,
        search_type=request.search_type,
        top_k=request.top_k,
        threshold=request.threshold,
        filters=filters if filters else None,
        sort_by=request.sort_by,
        sort_order=request.sort_order,
        user_id=current_user.id
    )
    
    return {
        "results": results.items,
        "total": results.total,
        "page": results.page,
        "page_size": results.page_size,
        "search_time_ms": results.search_time_ms
    }
```

### 3.3 搜索服务实现

```python
# services/search_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass

@dataclass
class SearchResult:
    items: List[Dict[str, Any]]
    total: int
    page: int
    page_size: int
    search_time_ms: float


class SearchService:
    """高级搜索服务"""
    
    def __init__(
        self,
        vector_store: VectorStore,
        document_repo: DocumentRepository,
        embedding_service: EmbeddingService
    ):
        self.vector_store = vector_store
        self.document_repo = document_repo
        self.embedding_service = embedding_service
    
    async def advanced_search(
        self,
        query: str,
        search_type: str,
        top_k: int,
        threshold: float,
        filters: Optional[Dict[str, Any]],
        sort_by: str,
        sort_order: str,
        user_id: str
    ) -> SearchResult:
        """执行高级搜索"""
        import time
        start_time = time.time()
        
        # 1. 执行向量/混合搜索
        if search_type == "semantic":
            vector_results = await self._semantic_search(
                query, top_k * 2, threshold, user_id
            )
        elif search_type == "hybrid":
            vector_results = await self._hybrid_search(
                query, top_k * 2, threshold, user_id
            )
        else:
            vector_results = []
        
        # 2. 获取文档元数据并应用过滤器
        document_ids = [r["document_id"] for r in vector_results]
        documents = await self.document_repo.get_by_ids(document_ids)
        
        # 3. 应用元数据过滤器
        if filters:
            documents = self._apply_filters(documents, filters)
        
        # 4. 构建搜索结果
        results = []
        for doc in documents:
            vector_result = next(
                (r for r in vector_results if r["document_id"] == doc.id),
                None
            )
            if vector_result:
                results.append({
                    **doc.to_dict(),
                    "score": vector_result["score"],
                    "highlights": vector_result.get("highlights", [])
                })
        
        # 5. 应用排序
        results = self._apply_sorting(results, sort_by, sort_order)
        
        # 6. 分页
        total = len(results)
        results = results[:top_k]
        
        search_time = (time.time() - start_time) * 1000
        
        return SearchResult(
            items=results,
            total=total,
            page=1,
            page_size=top_k,
            search_time_ms=round(search_time, 2)
        )
    
    def _apply_filters(
        self, 
        documents: List[Document], 
        filters: Dict[str, Any]
    ) -> List[Document]:
        """应用过滤器"""
        result = documents
        
        if "document_types" in filters:
            result = [d for d in result if d.type in filters["document_types"]]
        
        if "date_range" in filters:
            date_filter = filters["date_range"]
            if date_filter.get("from"):
                result = [d for d in result if d.created_at >= date_filter["from"]]
            if date_filter.get("to"):
                result = [d for d in result if d.created_at <= date_filter["to"]]
        
        if "tags" in filters:
            result = [
                d for d in result 
                if any(tag in d.tags for tag in filters["tags"])
            ]
        
        if "folders" in filters:
            result = [d for d in result if d.folder_id in filters["folders"]]
        
        if "size_range" in filters:
            size_filter = filters["size_range"]
            if size_filter.get("min") is not None:
                result = [d for d in result if d.size >= size_filter["min"]]
            if size_filter.get("max") is not None:
                result = [d for d in result if d.size <= size_filter["max"]]
        
        return result
    
    def _apply_sorting(
        self,
        results: List[Dict[str, Any]],
        sort_by: str,
        sort_order: str
    ) -> List[Dict[str, Any]]:
        """应用排序"""
        reverse = sort_order == "desc"
        
        if sort_by == "relevance":
            return sorted(results, key=lambda x: x["score"], reverse=reverse)
        elif sort_by == "created_at":
            return sorted(results, key=lambda x: x["created_at"], reverse=reverse)
        elif sort_by == "updated_at":
            return sorted(results, key=lambda x: x["updated_at"], reverse=reverse)
        elif sort_by == "title":
            return sorted(results, key=lambda x: x["title"].lower(), reverse=reverse)
        elif sort_by == "size":
            return sorted(results, key=lambda x: x.get("size", 0), reverse=reverse)
        
        return results
```

---

## ✅ 四、批量操作

### 4.1 批量操作工具栏组件

```typescript
// components/BatchOperationToolbar.tsx
import { 
  Button, 
  Space, 
  Popconfirm, 
  Dropdown, 
  Modal,
  message 
} from 'antd';
import { 
  DeleteOutlined, 
  FolderOutlined, 
  TagOutlined,
  DownloadOutlined,
  MoreOutlined
} from '@ant-design/icons';
import { useState } from 'react';
import { MoveToFolderModal } from './MoveToFolderModal';
import { AddTagsModal } from './AddTagsModal';

interface BatchOperationToolbarProps {
  selectedIds: string[];
  onClearSelection: () => void;
  onDelete: (ids: string[]) => Promise<void>;
  onMove: (ids: string[], folderId: string) => Promise<void>;
  onAddTags: (ids: string[], tags: string[]) => Promise<void>;
  onExport: (ids: string[]) => Promise<void>;
}

export function BatchOperationToolbar({
  selectedIds,
  onClearSelection,
  onDelete,
  onMove,
  onAddTags,
  onExport
}: BatchOperationToolbarProps) {
  const [moveModalVisible, setMoveModalVisible] = useState(false);
  const [tagsModalVisible, setTagsModalVisible] = useState(false);

  const handleDelete = async () => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除选中的 ${selectedIds.length} 个文档吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await onDelete(selectedIds);
          message.success(`成功删除 ${selectedIds.length} 个文档`);
          onClearSelection();
        } catch (error) {
          message.error('删除失败: ' + error.message);
        }
      }
    });
  };

  const handleMove = async (folderId: string) => {
    try {
      await onMove(selectedIds, folderId);
      message.success('移动成功');
      setMoveModalVisible(false);
      onClearSelection();
    } catch (error) {
      message.error('移动失败: ' + error.message);
    }
  };

  const handleAddTags = async (tags: string[]) => {
    try {
      await onAddTags(selectedIds, tags);
      message.success('标签添加成功');
      setTagsModalVisible(false);
      onClearSelection();
    } catch (error) {
      message.error('添加标签失败: ' + error.message);
    }
  };

  const moreMenuItems = [
    {
      key: 'export',
      icon: <DownloadOutlined />,
      label: '导出选中',
      onClick: () => onExport(selectedIds)
    }
  ];

  if (selectedIds.length === 0) return null;

  return (
    <>
      <div className="batch-operation-toolbar">
        <Space>
          <span className="selected-count">
            已选择 {selectedIds.length} 项
          </span>
          
          <Button onClick={onClearSelection}>
            取消选择
          </Button>

          <Popconfirm
            title="批量移动"
            description="将选中文档移动到指定文件夹"
            onConfirm={() => setMoveModalVisible(true)}
            okText="确定"
            cancelText="取消"
          >
            <Button icon={<FolderOutlined />}>
              移动到
            </Button>
          </Popconfirm>

          <Button 
            icon={<TagOutlined />}
            onClick={() => setTagsModalVisible(true)}
          >
            添加标签
          </Button>

          <Button 
            danger 
            icon={<DeleteOutlined />}
            onClick={handleDelete}
          >
            删除
          </Button>

          <Dropdown menu={{ items: moreMenuItems }} placement="bottomRight">
            <Button icon={<MoreOutlined />} />
          </Dropdown>
        </Space>
      </div>

      <MoveToFolderModal
        visible={moveModalVisible}
        onCancel={() => setMoveModalVisible(false)}
        onConfirm={handleMove}
      />

      <AddTagsModal
        visible={tagsModalVisible}
        onCancel={() => setTagsModalVisible(false)}
        onConfirm={handleAddTags}
      />
    </>
  );
}
```

**实现特性：**
- ✅ 批量选择计数显示
- ✅ 批量移动到文件夹
- ✅ 批量添加标签
- ✅ 批量删除（带确认）
- ✅ 批量导出
- ✅ 取消选择

### 4.2 批量选择 Hook

```typescript
// hooks/useBatchSelection.ts
import { useState, useCallback } from 'react';

interface UseBatchSelectionReturn {
  selectedIds: string[];
  isSelected: (id: string) => boolean;
  toggleSelection: (id: string) => void;
  selectAll: (ids: string[]) => void;
  deselectAll: () => void;
  selectRange: (ids: string[], startId: string, endId: string) => void;
}

export function useBatchSelection(): UseBatchSelectionReturn {
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  const isSelected = useCallback((id: string) => {
    return selectedIds.includes(id);
  }, [selectedIds]);

  const toggleSelection = useCallback((id: string) => {
    setSelectedIds(prev => {
      if (prev.includes(id)) {
        return prev.filter(item => item !== id);
      }
      return [...prev, id];
    });
  }, []);

  const selectAll = useCallback((ids: string[]) => {
    setSelectedIds(ids);
  }, []);

  const deselectAll = useCallback(() => {
    setSelectedIds([]);
  }, []);

  const selectRange = useCallback((ids: string[], startId: string, endId: string) => {
    const startIndex = ids.indexOf(startId);
    const endIndex = ids.indexOf(endId);
    
    if (startIndex === -1 || endIndex === -1) return;
    
    const [min, max] = [Math.min(startIndex, endIndex), Math.max(startIndex, endIndex)];
    const rangeIds = ids.slice(min, max + 1);
    
    setSelectedIds(prev => {
      const newSelection = new Set(prev);
      rangeIds.forEach(id => newSelection.add(id));
      return Array.from(newSelection);
    });
  }, []);

  return {
    selectedIds,
    isSelected,
    toggleSelection,
    selectAll,
    deselectAll,
    selectRange
  };
}
```

### 4.3 后端批量操作 API

```python
# api/routers/batch.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel

from ...services.batch_service import BatchService
from ...core.auth import get_current_user

router = APIRouter(prefix="/batch", tags=["Batch Operations"])


class BatchDeleteRequest(BaseModel):
    document_ids: List[str]


class BatchMoveRequest(BaseModel):
    document_ids: List[str]
    target_folder_id: str


class BatchTagRequest(BaseModel):
    document_ids: List[str]
    tags: List[str]
    operation: str = "add"  # add, remove, set


@router.post("/delete")
async def batch_delete(
    request: BatchDeleteRequest,
    current_user: User = Depends(get_current_user),
    batch_service: BatchService = Depends(get_batch_service)
):
    """批量删除文档"""
    result = await batch_service.delete_documents(
        document_ids=request.document_ids,
        user_id=current_user.id
    )
    return {
        "success": True,
        "deleted_count": result.deleted_count,
        "failed_ids": result.failed_ids
    }


@router.post("/move")
async def batch_move(
    request: BatchMoveRequest,
    current_user: User = Depends(get_current_user),
    batch_service: BatchService = Depends(get_batch_service)
):
    """批量移动文档"""
    result = await batch_service.move_documents(
        document_ids=request.document_ids,
        target_folder_id=request.target_folder_id,
        user_id=current_user.id
    )
    return {
        "success": True,
        "moved_count": result.moved_count,
        "failed_ids": result.failed_ids
    }


@router.post("/tags")
async def batch_manage_tags(
    request: BatchTagRequest,
    current_user: User = Depends(get_current_user),
    batch_service: BatchService = Depends(get_batch_service)
):
    """批量管理标签"""
    result = await batch_service.manage_tags(
        document_ids=request.document_ids,
        tags=request.tags,
        operation=request.operation,
        user_id=current_user.id
    )
    return {
        "success": True,
        "updated_count": result.updated_count,
        "failed_ids": result.failed_ids
    }
```

### 4.4 批量操作服务

```python
# services/batch_service.py
from typing import List, Dict, Any
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession

@dataclass
class BatchResult:
    success_count: int
    failed_ids: List[str]
    errors: Dict[str, str]


class BatchService:
    """批量操作服务"""
    
    def __init__(
        self,
        db: AsyncSession,
        document_repo: DocumentRepository,
        vector_store: VectorStore,
        celery_app: Celery
    ):
        self.db = db
        self.document_repo = document_repo
        self.vector_store = vector_store
        self.celery_app = celery_app
    
    async def delete_documents(
        self,
        document_ids: List[str],
        user_id: str
    ) -> BatchResult:
        """批量删除文档"""
        failed_ids = []
        errors = {}
        
        for doc_id in document_ids:
            try:
                # 验证权限
                doc = await self.document_repo.get(doc_id)
                if not doc or doc.user_id != user_id:
                    failed_ids.append(doc_id)
                    errors[doc_id] = "无权删除或文档不存在"
                    continue
                
                # 异步删除任务
                self.celery_app.send_task(
                    'tasks.delete_document',
                    args=[doc_id],
                    queue='documents'
                )
                
            except Exception as e:
                failed_ids.append(doc_id)
                errors[doc_id] = str(e)
        
        return BatchResult(
            success_count=len(document_ids) - len(failed_ids),
            failed_ids=failed_ids,
            errors=errors
        )
    
    async def move_documents(
        self,
        document_ids: List[str],
        target_folder_id: str,
        user_id: str
    ) -> BatchResult:
        """批量移动文档"""
        failed_ids = []
        errors = {}
        
        # 验证目标文件夹
        folder = await self.folder_repo.get(target_folder_id)
        if not folder or folder.user_id != user_id:
            return BatchResult(
                success_count=0,
                failed_ids=document_ids,
                errors={id: "目标文件夹不存在或无权限" for id in document_ids}
            )
        
        # 批量更新
        try:
            updated = await self.document_repo.batch_update_folder(
                document_ids=document_ids,
                folder_id=target_folder_id,
                user_id=user_id
            )
            failed_ids = list(set(document_ids) - set(updated))
        except Exception as e:
            errors = {id: str(e) for id in document_ids}
            failed_ids = document_ids
        
        return BatchResult(
            success_count=len(document_ids) - len(failed_ids),
            failed_ids=failed_ids,
            errors=errors
        )
    
    async def manage_tags(
        self,
        document_ids: List[str],
        tags: List[str],
        operation: str,
        user_id: str
    ) -> BatchResult:
        """批量管理标签"""
        failed_ids = []
        errors = {}
        
        for doc_id in document_ids:
            try:
                doc = await self.document_repo.get(doc_id)
                if not doc or doc.user_id != user_id:
                    failed_ids.append(doc_id)
                    errors[doc_id] = "无权修改或文档不存在"
                    continue
                
                if operation == "add":
                    doc.tags = list(set(doc.tags + tags))
                elif operation == "remove":
                    doc.tags = [t for t in doc.tags if t not in tags]
                elif operation == "set":
                    doc.tags = tags
                
                await self.db.commit()
                
            except Exception as e:
                failed_ids.append(doc_id)
                errors[doc_id] = str(e)
        
        return BatchResult(
            success_count=len(document_ids) - len(failed_ids),
            failed_ids=failed_ids,
            errors=errors
        )
```

---

## ✅ 五、导入/导出功能

### 5.1 导入组件

```typescript
// components/DocumentImporter.tsx
import { 
  Upload, 
  Button, 
  Modal, 
  Progress, 
  List, 
  Tag,
  Space,
  Alert,
  Select
} from 'antd';
import { 
  UploadOutlined, 
  FileOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined
} from '@ant-design/icons';
import { useState } from 'react';
import { useWebSocketStore } from '../stores/websocketStore';

interface ImportFile {
  uid: string;
  name: string;
  size: number;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error';
  progress: number;
  taskId?: string;
  error?: string;
}

interface DocumentImporterProps {
  visible: boolean;
  onCancel: () => void;
  folderId?: string;
}

export function DocumentImporter({ visible, onCancel, folderId }: DocumentImporterProps) {
  const [files, setFiles] = useState<ImportFile[]>([]);
  const [targetFolder, setTargetFolder] = useState(folderId);
  const { taskProgress } = useWebSocketStore();

  const handleUpload = async (file: File) => {
    const newFile: ImportFile = {
      uid: file.uid,
      name: file.name,
      size: file.size,
      status: 'pending',
      progress: 0
    };
    
    setFiles(prev => [...prev, newFile]);
    
    // 上传文件
    const formData = new FormData();
    formData.append('file', file);
    formData.append('folder_id', targetFolder || '');
    
    try {
      setFiles(prev => 
        prev.map(f => f.uid === file.uid ? { ...f, status: 'uploading' } : f)
      );
      
      const response = await fetch('/api/documents/import', {
        method: 'POST',
        body: formData
      });
      
      const result = await response.json();
      
      if (result.task_id) {
        setFiles(prev => 
          prev.map(f => 
            f.uid === file.uid 
              ? { ...f, taskId: result.task_id, status: 'processing' } 
              : f
          )
        );
      }
    } catch (error) {
      setFiles(prev => 
        prev.map(f => 
          f.uid === file.uid 
            ? { ...f, status: 'error', error: error.message } 
            : f
        )
      );
    }
    
    return false; // 阻止默认上传行为
  };

  // 监听任务进度
  files.forEach(file => {
    if (file.taskId && taskProgress.has(file.taskId)) {
      const progress = taskProgress.get(file.taskId);
      const fileIndex = files.findIndex(f => f.taskId === file.taskId);
      
      if (fileIndex !== -1 && progress) {
        const updatedFiles = [...files];
        updatedFiles[fileIndex].progress = progress.progress;
        
        if (progress.status === 'completed') {
          updatedFiles[fileIndex].status = 'completed';
        } else if (progress.status === 'failed') {
          updatedFiles[fileIndex].status = 'error';
          updatedFiles[fileIndex].error = progress.error;
        }
        
        setFiles(updatedFiles);
      }
    }
  });

  const getStatusIcon = (status: ImportFile['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'uploading':
      case 'processing':
        return <LoadingOutlined style={{ color: '#1890ff' }} />;
      default:
        return <FileOutlined />;
    }
  };

  const completedCount = files.filter(f => f.status === 'completed').length;
  const errorCount = files.filter(f => f.status === 'error').length;
  const totalCount = files.length;

  return (
    <Modal
      title="导入文档"
      visible={visible}
      onCancel={onCancel}
      width={700}
      footer={[
        <Button key="close" onClick={onCancel}>
          关闭
        </Button>
      ]}
    >
      <Space direction="vertical" style={{ width: '100%' }}>
        <Select
          placeholder="选择目标文件夹"
          style={{ width: '100%' }}
          value={targetFolder}
          onChange={setTargetFolder}
          allowClear
        >
          {/* 文件夹选项 */}
        </Select>

        <Upload.Dragger
          multiple
          beforeUpload={handleUpload}
          accept=".pdf,.docx,.txt,.md,.json,.csv"
          showUploadList={false}
        >
          <p className="ant-upload-drag-icon">
            <UploadOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p className="ant-upload-hint">
            支持 PDF、Word、TXT、Markdown、JSON、CSV 格式
          </p>
        </Upload.Dragger>

        {totalCount > 0 && (
          <Alert
            message={`导入进度: ${completedCount} 成功, ${errorCount} 失败, 共 ${totalCount} 个文件`}
            type={errorCount > 0 ? 'warning' : 'info'}
            showIcon
          />
        )}

        <List
          className="import-file-list"
          dataSource={files}
          renderItem={file => (
            <List.Item>
              <Space style={{ width: '100%' }}>
                {getStatusIcon(file.status)}
                <span className="file-name">{file.name}</span>
                <Tag>{(file.size / 1024).toFixed(1)} KB</Tag>
                
                {(file.status === 'uploading' || file.status === 'processing') && (
                  <Progress 
                    percent={file.progress} 
                    size="small" 
                    style={{ width: 100 }}
                  />
                )}
                
                {file.status === 'completed' && (
                  <Tag color="success">完成</Tag>
                )}
                
                {file.status === 'error' && (
                  <Tag color="error" title={file.error}>失败</Tag>
                )}
              </Space>
            </List.Item>
          )}
        />
      </Space>
    </Modal>
  );
}
```

**实现特性：**
- ✅ 多文件拖拽上传
- ✅ 支持多种格式（PDF/Word/TXT/MD/JSON/CSV）
- ✅ 目标文件夹选择
- ✅ 实时进度跟踪（WebSocket）
- ✅ 批量状态展示
- ✅ 导入结果统计

### 5.2 导出组件

```typescript
// components/DocumentExporter.tsx
import { 
  Modal, 
  Form, 
  Select, 
  Radio, 
  Checkbox,
  Button,
  message,
  Alert
} from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { useState } from 'react';

interface ExportOptions {
  format: 'pdf' | 'docx' | 'txt' | 'json' | 'csv';
  includeMetadata: boolean;
  includeContent: boolean;
  includeEmbeddings: boolean;
  compression: 'none' | 'zip';
}

interface DocumentExporterProps {
  visible: boolean;
  documentIds: string[];
  onCancel: () => void;
}

export function DocumentExporter({ 
  visible, 
  documentIds, 
  onCancel 
}: DocumentExporterProps) {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handleExport = async (values: ExportOptions) => {
    setLoading(true);
    
    try {
      const response = await fetch('/api/documents/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_ids: documentIds,
          ...values
        })
      });
      
      if (!response.ok) throw new Error('导出失败');
      
      // 下载文件
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `documents_export_${Date.now()}.${values.compression === 'zip' ? 'zip' : values.format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      message.success('导出成功');
      onCancel();
    } catch (error) {
      message.error('导出失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      title="导出文档"
      visible={visible}
      onCancel={onCancel}
      footer={null}
    >
      <Alert
        message={`将导出 ${documentIds.length} 个文档`}
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />
      
      <Form
        form={form}
        layout="vertical"
        onFinish={handleExport}
        initialValues={{
          format: 'pdf',
          includeMetadata: true,
          includeContent: true,
          includeEmbeddings: false,
          compression: 'zip'
        }}
      >
        <Form.Item
          name="format"
          label="导出格式"
          rules={[{ required: true }]}
        >
          <Radio.Group>
            <Radio.Button value="pdf">PDF</Radio.Button>
            <Radio.Button value="docx">Word</Radio.Button>
            <Radio.Button value="txt">纯文本</Radio.Button>
            <Radio.Button value="json">JSON</Radio.Button>
            <Radio.Button value="csv">CSV</Radio.Button>
          </Radio.Group>
        </Form.Item>

        <Form.Item name="includeMetadata" valuePropName="checked">
          <Checkbox>包含元数据（创建时间、标签等）</Checkbox>
        </Form.Item>

        <Form.Item name="includeContent" valuePropName="checked">
          <Checkbox>包含文档内容</Checkbox>
        </Form.Item>

        <Form.Item name="includeEmbeddings" valuePropName="checked">
          <Checkbox>包含向量嵌入（仅 JSON 格式）</Checkbox>
        </Form.Item>

        <Form.Item name="compression" label="压缩方式">
          <Radio.Group>
            <Radio value="none">不压缩</Radio>
            <Radio value="zip">ZIP 压缩</Radio>
          </Radio.Group>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button type="primary" htmlType="submit" loading={loading} icon={<DownloadOutlined />}>
              导出
            </Button>
            <Button onClick={onCancel}>取消</Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  );
}
```

**实现特性：**
- ✅ 多格式导出（PDF/Word/TXT/JSON/CSV）
- ✅ 元数据/内容/向量可选导出
- ✅ ZIP 压缩选项
- ✅ 批量下载
- ✅ 导出进度反馈

### 5.3 后端导入服务

```python
# services/import_service.py
from typing import List, BinaryIO
from dataclasses import dataclass
import magic
import chardet

@dataclass
class ImportResult:
    document_id: str
    filename: str
    status: str  # success, error
    error_message: Optional[str] = None


class ImportService:
    """文档导入服务"""
    
    SUPPORTED_FORMATS = {
        'application/pdf': 'pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'text/plain': 'txt',
        'text/markdown': 'md',
        'application/json': 'json',
        'text/csv': 'csv'
    }
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    def __init__(
        self,
        document_repo: DocumentRepository,
        parser_service: ParserService,
        celery_app: Celery
    ):
        self.document_repo = document_repo
        self.parser_service = parser_service
        self.celery_app = celery_app
    
    async def import_document(
        self,
        file: BinaryIO,
        filename: str,
        folder_id: Optional[str],
        user_id: str
    ) -> ImportResult:
        """导入单个文档"""
        
        # 1. 验证文件
        validation = await self._validate_file(file, filename)
        if not validation.valid:
            return ImportResult(
                document_id="",
                filename=filename,
                status="error",
                error_message=validation.error
            )
        
        # 2. 保存文件
        file_path = await self._save_file(file, filename, user_id)
        
        # 3. 创建文档记录
        document = Document(
            title=filename,
            filename=filename,
            file_path=file_path,
            file_type=validation.file_type,
            file_size=validation.file_size,
            folder_id=folder_id,
            user_id=user_id,
            status="processing"
        )
        
        await self.document_repo.create(document)
        
        # 4. 触发异步处理任务
        task = self.celery_app.send_task(
            'tasks.process_document',
            args=[document.id],
            queue='documents'
        )
        
        return ImportResult(
            document_id=document.id,
            filename=filename,
            status="success"
        )
    
    async def _validate_file(
        self, 
        file: BinaryIO, 
        filename: str
    ) -> ValidationResult:
        """验证文件"""
        
        # 检查文件大小
        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > self.MAX_FILE_SIZE:
            return ValidationResult(
                valid=False,
                error=f"文件大小超过限制 ({self.MAX_FILE_SIZE / 1024 / 1024}MB)"
            )
        
        # 检测文件类型
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file.read(1024))
        file.seek(0)
        
        if file_type not in self.SUPPORTED_FORMATS:
            return ValidationResult(
                valid=False,
                error=f"不支持的文件类型: {file_type}"
            )
        
        return ValidationResult(
            valid=True,
            file_type=self.SUPPORTED_FORMATS[file_type],
            file_size=file_size
        )
```

### 5.4 后端导出服务

```python
# services/export_service.py
from typing import List, Optional
import io
import zipfile
from datetime import datetime


class ExportService:
    """文档导出服务"""
    
    def __init__(
        self,
        document_repo: DocumentRepository,
        parser_service: ParserService
    ):
        self.document_repo = document_repo
        self.parser_service = parser_service
    
    async def export_documents(
        self,
        document_ids: List[str],
        format: str,
        include_metadata: bool,
        include_content: bool,
        include_embeddings: bool,
        compression: str,
        user_id: str
    ) -> bytes:
        """导出文档"""
        
        # 获取文档
        documents = await self.document_repo.get_by_ids(document_ids)
        documents = [d for d in documents if d.user_id == user_id]
        
        if format == 'json':
            return await self._export_as_json(
                documents, include_metadata, include_content, include_embeddings
            )
        elif format == 'csv':
            return await self._export_as_csv(
                documents, include_metadata, include_content
            )
        elif format == 'txt':
            return await self._export_as_txt(documents, include_metadata)
        else:
            return await self._export_as_binary(
                documents, format, compression
            )
    
    async def _export_as_json(
        self,
        documents: List[Document],
        include_metadata: bool,
        include_content: bool,
        include_embeddings: bool
    ) -> bytes:
        """导出为 JSON"""
        import json
        
        data = []
        for doc in documents:
            item = {"id": doc.id, "title": doc.title}
            
            if include_metadata:
                item["metadata"] = {
                    "created_at": doc.created_at.isoformat(),
                    "updated_at": doc.updated_at.isoformat(),
                    "tags": doc.tags,
                    "folder_id": doc.folder_id
                }
            
            if include_content:
                item["content"] = doc.content
            
            if include_embeddings and doc.embeddings:
                item["embeddings"] = doc.embeddings
            
            data.append(item)
        
        return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
    
    async def _export_as_csv(
        self,
        documents: List[Document],
        include_metadata: bool,
        include_content: bool
    ) -> bytes:
        """导出为 CSV"""
        import csv
        
        output = io.StringIO()
        fieldnames = ['id', 'title']
        
        if include_metadata:
            fieldnames.extend(['created_at', 'updated_at', 'tags'])
        
        if include_content:
            fieldnames.append('content')
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for doc in documents:
            row = {'id': doc.id, 'title': doc.title}
            
            if include_metadata:
                row.update({
                    'created_at': doc.created_at.isoformat(),
                    'updated_at': doc.updated_at.isoformat(),
                    'tags': ','.join(doc.tags)
                })
            
            if include_content:
                row['content'] = doc.content[:10000]  # CSV 单元格限制
            
            writer.writerow(row)
        
        return output.getvalue().encode('utf-8')
    
    async def _export_as_zip(
        self,
        documents: List[Document],
        format: str
    ) -> bytes:
        """导出为 ZIP"""
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for doc in documents:
                # 添加原始文件
                if doc.file_path and os.path.exists(doc.file_path):
                    zip_file.write(
                        doc.file_path,
                        arcname=f"{doc.title}_{doc.id[:8]}.{doc.file_type}"
                    )
        
        zip_buffer.seek(0)
        return zip_buffer.getvalue()
```

---

## 📁 文件清单

### 新增/修改文件

```
skyone-shuge/
├── prd/
│   └── MVP_v3.0.11.md                    # ✅ 本 PRD 文档
│
├── architecture/
│   └── ARCHITECTURE_v3.0.11.md           # ✅ 架构文档 v3.0.11
│
├── src/frontend/src/
│   ├── pages/
│   │   ├── Login.tsx                     # ✅ 登录页面
│   │   └── Register.tsx                  # ✅ 注册页面
│   │
│   ├── components/
│   │   ├── AuthGuard.tsx                 # ✅ 路由守卫
│   │   ├── SemanticSearch.tsx            # ✅ 语义搜索组件
│   │   ├── SearchResults.tsx             # ✅ 搜索结果展示
│   │   ├── HighlightText.tsx             # ✅ 高亮文本
│   │   ├── AdvancedSearchFilters.tsx     # ✅ 高级搜索过滤
│   │   ├── BatchOperationToolbar.tsx     # ✅ 批量操作工具栏
│   │   ├── DocumentImporter.tsx          # ✅ 文档导入
│   │   └── DocumentExporter.tsx          # ✅ 文档导出
│   │
│   ├── stores/
│   │   ├── authStore.ts                  # ✅ 认证状态管理
│   │   └── searchStore.ts                # ✅ 搜索状态管理
│   │
│   ├── api/
│   │   ├── auth.ts                       # ✅ 认证 API
│   │   ├── client.ts                     # ✅ API 客户端（含拦截器）
│   │   └── search.ts                     # ✅ 搜索 API
│   │
│   └── hooks/
│       └── useBatchSelection.ts          # ✅ 批量选择 Hook
│
├── src/skyone_shuge/
│   ├── api/routers/
│   │   ├── auth.py                       # ✅ 认证路由
│   │   ├── search.py                     # ✅ 搜索路由
│   │   └── batch.py                      # ✅ 批量操作路由
│   │
│   ├── services/
│   │   ├── search_service.py             # ✅ 搜索服务
│   │   ├── batch_service.py              # ✅ 批量操作服务
│   │   ├── import_service.py             # ✅ 导入服务
│   │   └── export_service.py             # ✅ 导出服务
│   │
│   └── schemas/
│       ├── auth.py                       # ✅ 认证 Schema
│       └── search.py                     # ✅ 搜索 Schema
│
└── src/frontend/src/styles/
    └── auth.css                          # ✅ 认证页面样式
```

---

## 🎯 验收标准

| 功能 | 验收标准 | 状态 |
|------|----------|------|
| 用户注册与登录 | 表单验证完整、Token 自动刷新、路由守卫有效 | ✅ 已完成 |
| 向量搜索集成 | 语义/关键词/混合搜索、相似度可视化、结果高亮 | ✅ 已完成 |
| 高级搜索 | 多维度过滤、多种排序、缓存优化 | ✅ 已完成 |
| 批量操作 | 批量选择、移动、标签管理、删除、导出 | ✅ 已完成 |
| 导入/导出 | 多格式支持、进度跟踪、压缩选项 | ✅ 已完成 |

---

## 🚀 下一步 (v3.0.12)

- [ ] LibIndex One 同步服务
- [ ] 项目级管理
- [ ] 协作功能
- [ ] 插件系统
