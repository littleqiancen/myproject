import axios from 'axios'
import type {
  Project, Document, TestPoint, TestCase,
  BatchStatus, LLMModel, AppSettings, Notification,
  PaginatedResponse, KnowledgeBase, KnowledgeBaseDocument
} from '../types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,
})

// ==================== 项目 ====================
export const projectApi = {
  list: (skip = 0, limit = 20) =>
    api.get<PaginatedResponse<Project>>('/projects', { params: { skip, limit } }),

  get: (id: string) =>
    api.get<Project>(`/projects/${id}`),

  create: (data: { name: string; description?: string }) =>
    api.post<Project>('/projects', data),

  update: (id: string, data: { name?: string; description?: string }) =>
    api.put<Project>(`/projects/${id}`, data),

  delete: (id: string) =>
    api.delete(`/projects/${id}`),
}

// ==================== 文档 ====================
export const documentApi = {
  list: (projectId: string) =>
    api.get<PaginatedResponse<Document>>(`/projects/${projectId}/documents`),

  get: (id: string) =>
    api.get<Document>(`/documents/${id}`),

  upload: (projectId: string, files: File[]) => {
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    return api.post<Document[]>(`/projects/${projectId}/documents/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  delete: (id: string) =>
    api.delete(`/documents/${id}`),

  reparse: (id: string) =>
    api.post<Document>(`/documents/${id}/reparse`),
}

// ==================== 测试点 ====================
export const testPointApi = {
  list: (projectId: string, params?: {
    category?: string; priority?: string; status?: string;
    skip?: number; limit?: number
  }) =>
    api.get<PaginatedResponse<TestPoint>>(`/projects/${projectId}/test-points`, { params }),

  get: (id: string) =>
    api.get<TestPoint>(`/test-points/${id}`),

  create: (projectId: string, data: Partial<TestPoint>) =>
    api.post<TestPoint>(`/projects/${projectId}/test-points`, data),

  update: (id: string, data: Partial<TestPoint>) =>
    api.put<TestPoint>(`/test-points/${id}`, data),

  delete: (id: string) =>
    api.delete(`/test-points/${id}`),

  batchDelete: (ids: string[]) =>
    api.post('/test-points/batch-delete', { ids }),
}

// ==================== 测试用例 ====================
export const testCaseApi = {
  list: (projectId: string, params?: {
    test_point_id?: string; priority?: string;
    case_type?: string; status?: string;
    skip?: number; limit?: number
  }) =>
    api.get<PaginatedResponse<TestCase>>(`/projects/${projectId}/test-cases`, { params }),

  get: (id: string) =>
    api.get<TestCase>(`/test-cases/${id}`),

  update: (id: string, data: Partial<TestCase>) =>
    api.put<TestCase>(`/test-cases/${id}`, data),

  delete: (id: string) =>
    api.delete(`/test-cases/${id}`),

  export: (projectId: string) =>
    api.get(`/projects/${projectId}/test-cases/export`, { responseType: 'blob' }),
}

// ==================== 知识库 ====================
export const knowledgeBaseApi = {
  list: (projectId: string) =>
    api.get<PaginatedResponse<KnowledgeBase>>(`/projects/${projectId}/knowledge-bases`),

  get: (id: string) =>
    api.get<KnowledgeBase>(`/knowledge-bases/${id}`),

  create: (projectId: string, data: { name: string; description?: string }) =>
    api.post<KnowledgeBase>(`/projects/${projectId}/knowledge-bases`, data),

  update: (id: string, data: { name?: string; description?: string }) =>
    api.put<KnowledgeBase>(`/knowledge-bases/${id}`, data),

  delete: (id: string) =>
    api.delete(`/knowledge-bases/${id}`),

  uploadDocuments: (kbId: string, files: File[]) => {
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    return api.post<KnowledgeBaseDocument[]>(`/knowledge-bases/${kbId}/documents/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  listDocuments: (kbId: string) =>
    api.get<PaginatedResponse<KnowledgeBaseDocument>>(`/knowledge-bases/${kbId}/documents`),

  deleteDocument: (docId: string) =>
    api.delete(`/knowledge-base-documents/${docId}`),
}

// ==================== AI 操作 ====================
export const aiApi = {
  extractTestPoints: (projectId: string, data: {
    document_ids: string[]; llm_model?: string; knowledge_base_ids?: string[]
  }) =>
    api.post<BatchStatus>(`/projects/${projectId}/ai/extract-test-points`, data),

  regenerateTestPoints: (projectId: string, data: {
    document_ids: string[]; existing_point_ids?: string[];
    feedback?: string; llm_model?: string; knowledge_base_ids?: string[]
  }) =>
    api.post<BatchStatus>(`/projects/${projectId}/ai/regenerate-test-points`, data),

  generateTestCases: (projectId: string, data: {
    test_point_ids: string[]; llm_model?: string; knowledge_base_ids?: string[]
  }) =>
    api.post<BatchStatus>(`/projects/${projectId}/ai/generate-test-cases`, data),

  getBatchStatus: (batchId: string) =>
    api.get<BatchStatus>(`/ai/batches/${batchId}`),

  getRunningBatches: (projectId: string) =>
    api.get<BatchStatus[]>(`/projects/${projectId}/ai/running-batches`),

  getModels: () =>
    api.get<LLMModel[]>('/ai/models'),
}

// ==================== 设置与通知 ====================
export const settingsApi = {
  get: () =>
    api.get<AppSettings>('/settings'),

  update: (data: Partial<{
    default_llm_model: string; llm_api_base: string;
    openai_api_key: string; anthropic_api_key: string;
    feishu_webhook_url: string; feishu_webhook_secret: string
  }>) =>
    api.put<AppSettings>('/settings', data),
}

export const notificationApi = {
  list: (projectId: string) =>
    api.get<PaginatedResponse<Notification>>(`/projects/${projectId}/notifications`),

  test: (webhookUrl: string, webhookSecret?: string) =>
    api.post('/notifications/test', { webhook_url: webhookUrl, webhook_secret: webhookSecret }),
}

export default api
