// API 响应类型定义

export interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  created_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Document {
  id: string;
  user_id: string;
  title: string;
  original_filename: string;
  file_size: number | null;
  mime_type: string | null;
  word_count: number;
  page_count: number;
  summary: string | null;
  is_processed: boolean;
  created_at: string;
}

export interface DocumentDetail extends Document {
  content: string | null;
  metadata: Record<string, unknown>;
}

export interface KnowledgeNode {
  id: string;
  node_type: string;
  name: string;
  description: string | null;
  importance: number;
  document_id: string | null;
  created_at: string;
}

export interface KnowledgeRelation {
  id: string;
  source_id: string;
  target_id: string;
  relation_type: string;
  weight: number;
}

export interface KnowledgeGraph {
  nodes: KnowledgeNode[];
  edges: KnowledgeRelation[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  description: string | null;
  importance: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  weight: number;
}

export interface VisualizationGraph {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  document_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ChatResponse {
  message: ChatMessage;
  session_id: string;
}

export interface LearningUnit {
  id: string;
  path_id: string;
  title: string;
  description: string | null;
  content: string | null;
  order_index: number;
  duration_minutes: number;
  difficulty: string;
  is_completed: boolean;
  completed_at: string | null;
}

export interface LearningPath {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  goal: string | null;
  difficulty: string;
  status: string;
  progress: number;
  created_at: string;
  units: LearningUnit[];
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
  success?: boolean;
}
