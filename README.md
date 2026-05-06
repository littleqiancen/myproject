# CaseGen - AI 驱动的测试用例生成平台

从 PRD 文档一键提取测试点并生成可执行测试用例，支持 RAG 知识库增强生成质量。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy 2.0 (async) + SQLite |
| 前端 | Vue 3 + Vite + Element Plus + TypeScript + Pinia |
| AI | LiteLLM（支持 OpenAI / Anthropic / DeepSeek 等 100+ 模型） |
| RAG | ChromaDB + sentence-transformers（本地 Embedding） |
| 部署 | Docker Compose |

## 核心功能

- 多格式文档上传（PDF / DOCX / Markdown）
- AI 自动提取 PRD 测试点
- AI 自动生成测试用例
- RAG 知识库管理 — 上传参考资料增强生成准确率和覆盖度
- 测试点/用例手动编辑与再生成
- 测试用例导出 Excel
- 飞书 Webhook 通知
- 后台异步生成 + 批次任务追踪
- 系统设置持久化（API Key、模型、Webhook 重启后保留）
- 自定义 LLM API 代理地址（支持 SiliconFlow 等第三方平台）

## 快速开始

### 方式一：本地开发（推荐）

**前置要求：** Python 3.12+、Node.js 18+

无需安装数据库，使用 SQLite，首次启动自动建表。

**后端：**

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端：**

```bash
cd frontend
npm install
npm run dev
```

**配置：**

可通过以下任一方式配置 LLM：

1. **推荐：UI 设置页** — 启动后访问 http://localhost:5173 → 系统设置，填入 API Key 和模型，保存后自动持久化
2. 环境变量 — 项目根目录创建 `.env` 文件：
```bash
OPENAI_API_KEY=sk-xxx
# 可选：自定义代理地址
LLM_API_BASE=https://api.siliconflow.cn/v1
DEFAULT_LLM_MODEL=openai/gpt-4o
```

启动后访问：

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| API 文档 (Swagger) | http://localhost:8000/docs |

### 方式二：Docker Compose

```bash
# 1. 复制环境变量模板
cp .env.example .env

# 2. 编辑 .env，填入 LLM API Key（也可启动后在 UI 设置页配置）

# 3. 启动所有服务
docker-compose up -d
```

```bash
# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## 使用流程

```
创建项目 → 上传 PRD 文档 → [可选]创建知识库 → AI 提取测试点 → 审阅/编辑 → AI 生成测试用例 → 导出 Excel
```

### 页面说明

| 页面 | 路径 | 说明 |
|------|------|------|
| 项目列表 | `/` | 查看所有项目及统计数据 |
| 项目详情 | `/projects/:id` | 文档 / 测试点 / 知识库 / 测试用例 四个标签页 |
| 系统设置 | `/settings` | 配置 LLM 模型、API Key、代理地址、飞书 Webhook |

### 操作步骤

1. **创建项目** — 在项目列表页点击「新建项目」
2. **上传文档** — 进入项目详情，在「文档」标签页上传 PRD 文件（支持 PDF/DOCX/MD）
3. **创建知识库**（可选）— 在「知识库」标签页创建知识库，上传接口文档、历史用例等参考资料
4. **提取测试点** — 选择文档，点击「AI 提取测试点」，可选关联知识库增强生成
5. **审阅测试点** — 在「测试点」标签页查看、编辑、删除测试点，可带反馈重新生成
6. **生成用例** — 选择测试点，点击「一键生成测试用例」，可选关联知识库
7. **导出** — 在「测试用例」标签页查看用例，点击「导出 Excel」下载

> AI 生成过程在后台异步执行，可关闭进度弹窗继续其他操作。切换项目后返回时会自动恢复运行中任务的状态。

## API 接口

基础路径：`/api/v1`

### 项目

```
GET    /projects          # 项目列表（分页）
POST   /projects          # 创建项目
GET    /projects/{id}     # 项目详情
PUT    /projects/{id}     # 更新项目
DELETE /projects/{id}     # 删除项目
```

### 文档

```
POST   /projects/{pid}/documents/upload   # 上传文档
GET    /projects/{pid}/documents          # 文档列表
GET    /documents/{id}                    # 文档详情
DELETE /documents/{id}                    # 删除文档
POST   /documents/{id}/reparse           # 重新解析
```

### 测试点

```
GET    /projects/{pid}/test-points       # 测试点列表（支持筛选）
POST   /projects/{pid}/test-points       # 手动创建测试点
PUT    /test-points/{id}                 # 编辑测试点
DELETE /test-points/{id}                 # 删除测试点
POST   /test-points/batch-delete         # 批量删除
```

### 测试用例

```
GET    /projects/{pid}/test-cases        # 用例列表（支持筛选）
PUT    /test-cases/{id}                  # 编辑用例
DELETE /test-cases/{id}                  # 删除用例
GET    /projects/{pid}/test-cases/export # 导出 Excel
```

### 知识库

```
POST   /projects/{pid}/knowledge-bases                  # 创建知识库
GET    /projects/{pid}/knowledge-bases                  # 知识库列表
GET    /knowledge-bases/{id}                            # 知识库详情
PUT    /knowledge-bases/{id}                            # 更新知识库
DELETE /knowledge-bases/{id}                            # 删除知识库（含向量数据）
POST   /knowledge-bases/{id}/documents/upload           # 上传知识库文档
GET    /knowledge-bases/{id}/documents                  # 知识库文档列表
DELETE /knowledge-base-documents/{id}                   # 删除知识库文档
```

### AI 操作

```
POST   /projects/{pid}/ai/extract-test-points      # 从文档提取测试点（支持关联知识库）
POST   /projects/{pid}/ai/regenerate-test-points    # 带反馈重新生成测试点
POST   /projects/{pid}/ai/generate-test-cases       # 从测试点生成用例（支持关联知识库）
GET    /projects/{pid}/ai/running-batches           # 获取项目正在运行的批次
GET    /ai/batches/{batch_id}                       # 查询批次进度
GET    /ai/models                                   # 可用模型列表
```

### 设置与通知

```
GET    /settings                          # 获取系统设置（API Key 脱敏显示）
PUT    /settings                          # 更新设置（自动持久化）
GET    /projects/{pid}/notifications      # 通知记录
POST   /notifications/test                # 测试飞书 Webhook
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DATABASE_PATH` | SQLite 数据库文件路径 | `casegen.db` |
| `DEFAULT_LLM_MODEL` | 默认 LLM 模型 | `openai/gpt-4o` |
| `OPENAI_API_KEY` | OpenAI / 兼容 API Key | — |
| `ANTHROPIC_API_KEY` | Anthropic API Key | — |
| `LLM_API_BASE` | LLM 代理地址（可选） | — |
| `FEISHU_WEBHOOK_URL` | 飞书 Webhook 地址 | — |
| `FEISHU_WEBHOOK_SECRET` | 飞书 Webhook 签名密钥 | — |
| `CHROMADB_PATH` | ChromaDB 向量数据目录 | `chromadb_data` |
| `EMBEDDING_PROVIDER` | Embedding 提供商：`local` / `openai` | `local` |
| `EMBEDDING_MODEL` | Embedding 模型 | `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | 文本分块大小（字符） | `512` |
| `CHUNK_OVERLAP` | 分块重叠（字符） | `64` |
| `RAG_TOP_K` | RAG 检索返回数量 | `5` |
| `MAX_UPLOAD_SIZE_MB` | 文件上传大小限制 | `50` |
| `LOG_LEVEL` | 日志级别 | `INFO` |

> 通过 UI 设置页修改的配置会保存到 `backend/settings.json`，优先于环境变量，重启后保留。

## 项目结构

```
CaseGenerateProject/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI 入口
│   │   ├── config.py               # 配置管理（env + settings.json 持久化）
│   │   ├── database.py             # 数据库连接（SQLite async）
│   │   ├── models/                 # ORM 模型
│   │   │   ├── project.py
│   │   │   ├── document.py
│   │   │   ├── test_point.py
│   │   │   ├── test_case.py
│   │   │   ├── generation_batch.py
│   │   │   ├── notification.py
│   │   │   └── knowledge_base.py   # 知识库 + 知识库文档
│   │   ├── schemas/                # Pydantic 模型
│   │   ├── api/v1/                 # API 路由
│   │   │   ├── projects.py
│   │   │   ├── documents.py
│   │   │   ├── test_points.py
│   │   │   ├── test_cases.py
│   │   │   ├── knowledge_bases.py  # 知识库管理 API
│   │   │   └── ai_operations.py    # AI 操作 + 设置 + 通知
│   │   ├── services/               # 业务逻辑
│   │   │   ├── knowledge_base_service.py  # 知识库 CRUD
│   │   │   ├── rag_service.py             # ChromaDB 检索
│   │   │   └── ai/                        # AI 相关服务
│   │   │       ├── llm_client.py          # LiteLLM 封装
│   │   │       ├── embedding_service.py   # Embedding（local/openai）
│   │   │       ├── document_parser.py     # 文档解析
│   │   │       ├── prompts.py             # LLM 提示词
│   │   │       ├── test_point_extractor.py
│   │   │       └── test_case_generator.py
│   │   └── integrations/           # 外部集成（飞书）
│   ├── settings.json               # UI 配置持久化（自动生成）
│   ├── casegen.db                  # SQLite 数据库（自动生成）
│   ├── chromadb_data/              # ChromaDB 向量数据（自动生成）
│   ├── uploads/                    # 上传文件存储
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── ProjectList.vue     # 项目列表
│   │   │   ├── ProjectDetail.vue   # 项目详情（文档/测试点/知识库/用例）
│   │   │   └── Settings.vue        # 系统设置
│   │   ├── components/
│   │   │   ├── AppLayout.vue       # 全局布局
│   │   │   └── AiProgressModal.vue # AI 进度弹窗（支持后台运行）
│   │   ├── stores/                 # Pinia 状态管理
│   │   ├── api/                    # API 客户端
│   │   └── types/                  # TypeScript 类型
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── 方案设计.md
└── README.md
```

## License

MIT
