import axios from 'axios';
import { Token, User, Document, DocumentDetail, KnowledgeGraph, VisualizationGraph, ChatSession, ChatMessage, ChatResponse, LearningPath } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ 认证 API ============
export const authApi = {
  register: async (email: string, username: string, password: string): Promise<Token> => {
    const response = await api.post('/api/auth/register', { email, username, password });
    return response.data;
  },

  login: async (email: string, password: string): Promise<Token> => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    const response = await api.post('/api/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// ============ 文档 API ============
export const documentApi = {
  upload: async (file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  list: async (skip = 0, limit = 20): Promise<Document[]> => {
    const response = await api.get('/api/documents', { params: { skip, limit } });
    return response.data;
  },

  get: async (id: string): Promise<DocumentDetail> => {
    const response = await api.get(`/api/documents/${id}`);
    return response.data;
  },

  delete: async (id: string): Promise<void> => {
    await api.delete(`/api/documents/${id}`);
  },

  getContent: async (id: string): Promise<{ content: string; word_count: number; page_count: number }> => {
    const response = await api.get(`/api/documents/${id}/content`);
    return response.data;
  },
};

// ============ 知识图谱 API ============
export const knowledgeApi = {
  getGraph: async (documentId?: string): Promise<KnowledgeGraph> => {
    const response = await api.get('/api/knowledge/graph', { params: { document_id: documentId } });
    return response.data;
  },

  getVisualization: async (documentId?: string): Promise<VisualizationGraph> => {
    const response = await api.get('/api/knowledge/graph/visualization', { params: { document_id: documentId } });
    return response.data;
  },

  search: async (query: string): Promise<{ query: string; results: Array<{ id: string; name: string; type: string; description: string | null }> }> => {
    const response = await api.get('/api/knowledge/search', { params: { q: query } });
    return response.data;
  },

  getStats: async (): Promise<{ total_nodes: number; total_relations: number; nodes_by_type: Record<string, number> }> => {
    const response = await api.get('/api/knowledge/stats');
    return response.data;
  },
};

// ============ 聊天 API ============
export const chatApi = {
  createSession: async (title = '新对话', documentId?: string): Promise<ChatSession> => {
    const response = await api.post('/api/chat/sessions', { title, document_id: documentId });
    return response.data;
  },

  listSessions: async (): Promise<ChatSession[]> => {
    const response = await api.get('/api/chat/sessions');
    return response.data;
  },

  getMessages: async (sessionId: string): Promise<ChatMessage[]> => {
    const response = await api.get(`/api/chat/sessions/${sessionId}/messages`);
    return response.data;
  },

  sendMessage: async (message: string, sessionId?: string, documentId?: string): Promise<ChatResponse> => {
    const response = await api.post('/api/chat/message', { message, session_id: sessionId, document_id: documentId });
    return response.data;
  },

  deleteSession: async (sessionId: string): Promise<void> => {
    await api.delete(`/api/chat/sessions/${sessionId}`);
  },
};

// ============ 学习路径 API ============
export const learningApi = {
  createPath: async (data: { title: string; description?: string; goal?: string; difficulty?: string }): Promise<LearningPath> => {
    const response = await api.post('/api/learning/paths', data);
    return response.data;
  },

  generatePath: async (topic: string, difficulty = 'intermediate', durationHours = 10, documentIds?: string[]): Promise<LearningPath> => {
    const response = await api.post('/api/learning/paths/generate', {
      topic,
      difficulty,
      duration_hours: durationHours,
      document_ids: documentIds,
    });
    return response.data;
  },

  listPaths: async (): Promise<LearningPath[]> => {
    const response = await api.get('/api/learning/paths');
    return response.data;
  },

  getPath: async (pathId: string): Promise<LearningPath> => {
    const response = await api.get(`/api/learning/paths/${pathId}`);
    return response.data;
  },

  completeUnit: async (pathId: string, unitId: string): Promise<{ message: string; success: boolean }> => {
    const response = await api.put(`/api/learning/paths/${pathId}/units/${unitId}/complete`);
    return response.data;
  },

  deletePath: async (pathId: string): Promise<void> => {
    await api.delete(`/api/learning/paths/${pathId}`);
  },
};

export default api;
