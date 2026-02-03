// Document Store
//文档状态管理

import { create } from 'zustand';
import { documentApi, categoryApi, searchApi } from '../api';

interface Document {
  id: string;
  title: string;
  file_name: string;
  file_type: string;
  category_path?: string;
  status: string;
  updated_at: string;
}

interface Category {
  id: string;
  name: string;
  path: string;
  type: string;
  children?: Category[];
}

interface DocumentState {
  // 文档列表
  documents: Document[];
  total: number;
  page: number;
  loading: boolean;
  
  // 搜索
  searchQuery: string;
  searchResults: Document[];
  
  // 分类
  categories: Category[];
  selectedCategory: string | null;
  
  // 统计
  statistics: {
    total: number;
    pending: number;
    classified: number;
  };
  
  // Actions
  fetchDocuments: (params?: any) => Promise<void>;
  fetchCategories: () => Promise<void>;
  searchDocuments: (query: string) => Promise<void>;
  selectCategory: (categoryId: string | null) => void;
  fetchStatistics: () => Promise<void>;
  updateDocument: (id: string, data: any) => Promise<void>;
  deleteDocument: (id: string) => Promise<void>;
  classifyDocument: (id: string, force?: boolean) => Promise<void>;
}

export const useDocumentStore = create<DocumentState>((set, get) => ({
  // 初始状态
  documents: [],
  total: 0,
  page: 1,
  loading: false,
  searchQuery: '',
  searchResults: [],
  categories: [],
  selectedCategory: null,
  statistics: {
    total: 0,
    pending: 0,
    classified: 0,
  },
  
  // Actions
  fetchDocuments: async (params = {}) => {
    set({ loading: true });
    try {
      const { page, selectedCategory } = get();
      const response = await documentApi.list({
        ...params,
        page: params.page || page,
        category_id: selectedCategory,
      });
      
      set({
        documents: response.data,
        total: response.meta.total,
        page: response.meta.page,
        loading: false,
      });
    } catch (error) {
      console.error('获取文档列表失败:', error);
      set({ loading: false });
    }
  },
  
  fetchCategories: async () => {
    try {
      const response = await categoryApi.tree();
      set({ categories: response.data });
    } catch (error) {
      console.error('获取分类失败:', error);
    }
  },
  
  searchDocuments: async (query: string) => {
    set({ searchQuery: query });
    if (!query.trim()) {
      set({ searchResults: [] });
      return;
    }
    
    try {
      const response = await searchApi.search({ q: query });
      set({ searchResults: response.results });
    } catch (error) {
      console.error('搜索失败:', error);
    }
  },
  
  selectCategory: (categoryId: string | null) => {
    set({ selectedCategory: categoryId });
    get().fetchDocuments();
  },
  
  fetchStatistics: async () => {
    try {
      // 简化实现，实际应调用统计 API
      const response = await documentApi.list({ limit: 1 });
      set({
        statistics: {
          total: response.meta.total,
          pending: 0,
          classified: response.meta.total,
        },
      });
    } catch (error) {
      console.error('获取统计失败:', error);
    }
  },
  
  updateDocument: async (id: string, data: any) => {
    try {
      await documentApi.update(id, data);
      get().fetchDocuments();
    } catch (error) {
      console.error('更新文档失败:', error);
      throw error;
    }
  },
  
  deleteDocument: async (id: string) => {
    try {
      await documentApi.delete(id);
      get().fetchDocuments();
    } catch (error) {
      console.error('删除文档失败:', error);
      throw error;
    }
  },
  
  classifyDocument: async (id: string, force = false) => {
    try {
      await documentApi.classify(id, force);
      get().fetchDocuments();
    } catch (error) {
      console.error('分类文档失败:', error);
      throw error;
    }
  },
}));
