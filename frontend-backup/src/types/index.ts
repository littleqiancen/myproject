export interface Project {
  id: string
  name: string
  description: string | null
  created_at: string
  updated_at: string
  stats: ProjectStats
}

export interface ProjectStats {
  document_count: number
  test_point_count: number
  test_case_count: number
}

export interface Document {
  id: string
  project_id: string
  filename: string
  file_type: string
  file_path: string
  file_size: number | null
  raw_text: string | null
  parsed_markdown: string | null
  parse_status: string
  parse_error: string | null
  created_at: string
  updated_at: string
}

export interface TestPoint {
  id: string
  project_id: string
  document_id: string | null
  title: string
  description: string
  priority: string | null
  category: string | null
  preconditions: string | null
  expected_result: string | null
  source_context: string | null
  is_manual_edit: boolean
  generation_batch_id: string | null
  status: string
  sort_order: number
  created_at: string
  updated_at: string
  test_case_count: number
}

export interface TestStep {
  step_number: number
  action: string
  expected_result: string
}

export interface TestCase {
  id: string
  project_id: string
  test_point_id: string
  title: string
  preconditions: string | null
  steps: TestStep[]
  priority: string | null
  case_type: string | null
  status: string
  generation_batch_id: string | null
  created_at: string
  updated_at: string
  test_point_title: string | null
}

export interface BatchStatus {
  id: string
  batch_type: string
  status: string
  error_message: string | null
  token_usage: Record<string, number> | null
  started_at: string | null
  completed_at: string | null
}

export interface LLMModel {
  id: string
  name: string
  provider: string
}

export interface AppSettings {
  default_llm_model: string
  llm_api_base: string
  feishu_webhook_url: string
  feishu_webhook_secret: string
  openai_api_key_set: boolean
  anthropic_api_key_set: boolean
  openai_api_key: string
  anthropic_api_key: string
}

export interface Notification {
  id: string
  project_id: string
  event_type: string
  channel: string
  payload: Record<string, any> | null
  status: string
  error_message: string | null
  sent_at: string | null
  created_at: string
}

export interface KnowledgeBase {
  id: string
  project_id: string
  name: string
  description: string | null
  document_count: number
  chunk_count: number
  status: string
  created_at: string
  updated_at: string
}

export interface KnowledgeBaseDocument {
  id: string
  knowledge_base_id: string
  filename: string
  file_type: string
  file_size: number | null
  chunk_count: number
  status: string
  error_message: string | null
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
}
