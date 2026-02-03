// API Client
//API 客户端

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // 未授权，清除 token
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 文档 API
export const documentApi = {
  list: (params?: {
    page?: number;
    limit?: number;
    category_id?: string;
    status?: string;
    search?: string;
  }) => api.get('/documents', { params }),
  
  get: (id: string) => api.get(`/documents/${id}`),
  
  update: (id: string, data: any) => api.put(`/documents/${id}`, data),
  
  delete: (id: string) => api.delete(`/documents/${id}`),
  
  classify: (id: string, force?: boolean) => 
    api.get(`/documents/${id}/classify`, { params: { force } }),
  
  scan: (paths: string[], options?: {
    recursive?: boolean;
    auto_classify?: boolean;
  }) => api.post('/documents/scan', { paths, ...options }),
};

// 分类 API
export const categoryApi = {
  list: (params?: { parent_id?: string; type?: string }) =>
    api.get('/categories', { params }),
  
  tree: () => api.get('/categories/tree'),
  
  get: (id: string) => api.get(`/categories/${id}`),
  
  create: (data: { name: string; parent_id?: string; type?: string }) =>
    api.post('/categories', data),
  
  delete: (id: string) => api.delete(`/categories/${id}`),
};

// 搜索 API
export const searchApi = {
  search: (params: {
    q: string;
    category_id?: string;
    status?: string;
    page?: number;
    limit?: number;
  }) => api.get('/search', { params }),
  
  suggest: (q: string) =>
    api.get('/search/suggest', { params: { q } }),
};

// 健康检查
export const healthApi = {
  check: () => api.get('/health'),
};

// 导出 api 实例
export default api;
