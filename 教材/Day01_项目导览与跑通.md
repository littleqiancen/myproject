# Day 1：项目导览与跑通（从 0 开始）

目标：把项目跑起来、能解释“它在干什么”、知道从哪里读代码。

你今天要学会 3 件事：

1. 这是什么系统（输入/输出/用户价值）
2. 怎么跑起来并验证功能（不依赖“感觉”）
3. 代码从哪里开始读（入口文件、目录职责、主流程）

---

## 0. 你需要准备什么（新手版）

这个项目是典型的“前后端分离 Web 应用”：

- 后端：Python + FastAPI（提供 REST API）
- 前端：Vue3 + Vite（浏览器 UI）
- AI：调用大模型（通过统一封装）
- 数据：SQLite（业务数据）+ ChromaDB（向量库，用于 RAG 检索增强）

所以你需要 3 类环境：

1) Python（跑后端）

- 这个项目 README 建议：Python 3.12+
- 你不需要“会 Python”，但需要能运行命令

2) Node.js（跑前端）

- 建议：Node 18+

3) （可选）Docker（如果你想一条命令起全套）

如果你不熟这些名词也没关系：你先照着操作跑通，今天最重要的是建立“系统能跑 + 我知道入口在哪里”的安全感。

---

## 1. 这个系统到底做了什么

一句话：

> 你上传需求文档（PRD），系统解析文本并结合知识库检索（RAG），然后用大模型生成测试点和测试用例，最后支持导出。

把它拆成“输入 → 处理 → 输出”：

- 输入：
  - 项目信息（项目名等）
  - PRD 文档（PDF/DOCX/MD/TXT）
  - （可选）知识库资料（作为参考资料增强生成质量）
- 处理：
  - 文档解析：把 PDF/DOCX 转成可用文本
  - 分块/向量化：把知识库资料分块并 embedding 写入向量库
  - 检索增强：生成前从向量库取相关片段喂给大模型
  - LLM 生成：产出结构化 JSON（测试点/用例）
  - 落库：把结果写到数据库
- 输出：
  - 测试点列表
  - 测试用例列表
  - Excel 导出

最关键的“产品设计点”是：

> AI 生成不是同步阻塞的，而是异步批次（batch）任务：先返回一个批次 ID，后端后台慢慢生成，前端用轮询看到进度。

这是一个非常适合面试讲的工程点（后面 Day 3 会详细讲）。

---

## 2. 项目目录结构怎么读

你只需要先认识几条“路径导航线”，不要尝试一次读完全部代码。

### 2.1 根目录：先看说明和部署

- `README.md`：怎么运行、产品流程、界面入口
- `docker-compose.yml`：一键部署前后端
- `方案设计.md`：系统设计思路（建议当天至少通读一遍）
- `.env.example`：环境变量示例（不要把真实 Key 提交进代码库）

### 2.2 后端：`backend/app/`

你先记住 3 个入口：

- `backend/app/main.py`：FastAPI 应用入口（类似“后端 main 函数”）
- `backend/app/api/v1/router.py`：把所有 API 路由集中挂载到 `/api/v1`
- `backend/app/config.py`：配置系统（env + settings.json）

再记住 3 个核心目录：

- `backend/app/api/v1/`：接口层（HTTP 路由）
- `backend/app/services/`：业务服务层（真正干活的逻辑）
- `backend/app/models/`：数据库模型（表结构）

### 2.3 前端：`frontend/src/`

你先记住 3 个入口：

- `frontend/src/main.ts`：Vue 应用入口
- `frontend/src/router/index.ts`：页面路由
- `frontend/src/api/index.ts`：Axios API 封装（baseURL 通常指向 `/api/v1`）

---

## 3. 跑起来（两种方式）

你选一种就行：

- A：本地开发（推荐新手，报错更直观）
- B：Docker Compose（推荐想“快速全套起来”的人）

### 3.1 A：本地开发跑后端（Python）

在项目根目录下确认你能看到 `backend/` 文件夹。

下面是 **Windows 小白可直接照抄** 的完整流程（每一步都有“你应该看到什么”）：

#### 第 1 步：打开 PowerShell，并切到后端目录

```powershell
cd .\backend
```

你应该看到：当前目录变成 `...\CaseGenerateProject\backend`。

#### 第 2 步：创建虚拟环境（把 Python 依赖隔离开）

```powershell
python -m venv venv
```

你应该看到：当前目录出现一个 `venv\` 文件夹。

#### 第 3 步：激活虚拟环境

```powershell
venv\Scripts\activate
```

你应该看到：命令行前面多了 `(venv)`。

如果提示“脚本运行被禁止”，执行一次：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新执行激活命令。

#### 第 4 步：安装后端依赖

```powershell
pip install -r requirements.txt
```

你应该看到：安装一堆包，最后没有红色错误。

#### 第 5 步：启动后端服务

```powershell
uvicorn app.main:app --reload --port 8000
```

你应该看到类似日志：

```text
Uvicorn running on http://127.0.0.1:8000
```

#### 第 6 步：验证后端真的 OK（不是“我觉得 OK”）

打开浏览器访问：

- `http://localhost:8000/health`（应该返回 `{"status":"ok"}`）
- `http://localhost:8000/docs`（应该看到 Swagger 页面）

如果 `8000` 端口被占用：

- 换一个端口，例如：`--port 8001`

### 3.1.1 新手常见坑：`.env` 放哪里？（一定要读）

这个项目的后端配置通过 `backend/app/config.py` 读取 `.env`。

你现在的仓库里 `.env` 在项目根目录（`CaseGenerateProject/.env`）。

但如果你按照 README 的方式 `cd backend` 再启动，后端默认会从 **当前工作目录** 去找 `.env`。

对新手来说最简单的做法是二选一：

- 方案 A（推荐）：**用 UI 设置页配置模型与 Key**，保存后会写入 `backend/settings.json`，后端会自动读取（不用操心 `.env`）
- 方案 B：把根目录 `.env` 复制一份到 `backend/.env`（仅本地开发，别提交 Key）

你可以先用方案 A，把系统跑通最重要。

你可以参考 `README.md` 中的命令。通常会类似：

```bash
uvicorn app.main:app --reload --port 8000
```

你需要知道这句话的含义：

- `uvicorn`：ASGI 服务器（让 FastAPI 对外提供 HTTP）
- `app.main:app`：去 `backend/app/main.py` 里找变量名叫 `app` 的 FastAPI 实例
- `--reload`：开发模式，改代码自动重启
- `--port 8000`：端口 8000

验证后端是否启动成功：

- 打开浏览器访问 `http://localhost:8000/docs`
- 如果你看到 Swagger UI（可交互 API 文档），说明后端 OK

为什么先看 `/docs`？

- 因为它不依赖前端
- 能直观看到有哪些 API、入参/出参是什么
- 面试时你也可以用它快速演示

### 3.2 A：本地开发跑前端（Node）

进入 `frontend/`，安装依赖并启动。

如果你刚才在 `backend/`，先回到根目录再进入前端：

```powershell
cd ..
cd .\frontend
```

然后执行：

```powershell
npm install
npm run dev
```

你应该看到类似：

```text
Local:   http://localhost:5173/
```

验证前端：

- 打开 `vite` 输出的本地地址（通常 `http://localhost:5173`）
- 做一个最小操作：打开页面、创建项目

如果前端报“接口跨域/请求失败”怎么办？

- 先确认后端是否能访问：`http://localhost:8000/docs`
- 再打开浏览器 F12 → Network，看前端请求的地址是不是 `/api/v1/...`
- 去看 `frontend/src/api/index.ts` 的 baseURL 是否是 `/api/v1`

---

## 3.4 小白必做：用 Swagger 手动点一次接口

为什么要点 Swagger？

- 你能确认后端 API 真能工作（排除前端问题）
- 你能理解 API 入参/出参（这是读代码的“地图”）

操作：

1) 打开 `http://localhost:8000/docs`
2) 找到 `GET /projects` 点开
3) 点 Try it out → Execute
4) 你应该看到 Response body（JSON）

如果这里都失败，你就不要去怪前端。

---

## 5.6 手把手：从“按钮”追到“后端函数”（第一次读代码就这么做）

你按下面步骤做一遍，就会发现读代码没那么玄学：

1) 在浏览器里点击一次“AI 提取测试点”
2) 打开 F12 → Network
3) 找到最新的请求，记下它的 URL（例如 `/api/v1/projects/1/ai/extract-test-points`）
4) 回到 IDE，全局搜索这个路径片段（例如搜索 `extract-test-points`）
5) 你会定位到后端文件 `backend/app/api/v1/ai_operations.py`
6) 继续在函数里找它调用了哪个 service（通常在 `backend/app/services/ai/`）

你今天不需要读懂所有逻辑，但你必须体验一次“从 UI → API → 代码”的追踪方式。

---

## 8. 从 0-1 你会怎么写这个项目（极简骨架，先看懂套路）

你现在看到的是一个完整项目。为了让你不觉得空，我给你一个“极简版本”的写法。

你只需要看懂它的结构，不要求你今天真的敲出来。

### 8.1 先写后端：一个能启动的 FastAPI

文件：`app/main.py`

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}
```

启动命令：

```bash
uvicorn app.main:app --reload --port 8000
```

### 8.2 再加前端：一个能请求后端的页面

你只要记住：前端最终就是发 HTTP 请求拿 JSON。

后面 Day2 开始我们会把“数据库、配置、路由分层”一步步加回来。

### 3.3 B：Docker Compose 一键启动（可选）

如果你安装了 Docker：

- 看根目录 `docker-compose.yml`
- 看前端 Nginx 反代规则 `frontend/nginx.conf`

你需要理解一件事：

> 前端容器里 Nginx 会把 `/api/` 请求转发到后端容器 `backend:8000`。

这样前端只要请求同域 `/api/...`，就没有浏览器跨域问题。

---

## 4. 最小闭环演示（你要能“跑通并讲出来”）

今天你至少要跑通一次：

1. 创建项目
2. 上传一份文档（PRD）
3. 点“提取测试点”（AI 操作）
4. 看到进度弹窗/轮询
5. 生成结束后看到测试点列表
6. （如果系统支持）再生成测试用例并导出

你现在还不需要理解 AI 里每一行代码，先建立“系统端到端能跑”的信心。

---

## 5. 从代码角度解释这个闭环（读代码路线）

你只需要顺着下面这条链路读：

### 5.1 后端入口

- `backend/app/main.py`
  - 创建 FastAPI app
  - 挂载路由（通常包含 `/api/v1`）
  - 应用启动时初始化数据库（创建表）

### 5.2 路由聚合

- `backend/app/api/v1/router.py`
  - 统一 `include_router(..., prefix="/api/v1")`

### 5.3 关键业务接口：AI 操作

- `backend/app/api/v1/ai_operations.py`
  - 提取测试点：`POST /projects/{id}/ai/extract-test-points`
  - 生成测试用例：`POST /projects/{id}/ai/generate-test-cases`
  - 批次查询：`GET /ai/batches/{batch_id}`

你现在只需要理解：

> 这些接口不是直接返回“结果”，而是先创建一个批次（batch），然后后台慢慢跑。

### 5.4 后台任务真正的逻辑在哪里

- `backend/app/services/ai/test_point_extractor.py`：提取测试点
- `backend/app/services/ai/test_case_generator.py`：生成测试用例

这些文件里通常会出现：

- 读项目文档内容
- （可选）做知识库检索增强
- 调用 LLM
- 解析结构化 JSON
- 写入数据库
- 更新批次状态

### 5.5 前端如何配合

- `frontend/src/api/index.ts`：封装请求
- `frontend/src/components/AiProgressModal.vue`：拿到 batchId 后每 2 秒轮询一次批次状态

你可以先把它理解成：

> 前端发起生成 → 后端说“我开始干了，给你一个编号” → 前端拿编号来问“干到哪了” → 干完再刷新页面。

---

## 6. 为什么要这样设计（新手能懂版）

### 6.1 为什么不用“同步接口一次性返回结果”？

因为 AI 生成很慢：

- 文档长
- RAG 检索 + LLM 调用可能多次
- 还要解析 JSON、落库

如果你用同步接口：

- 浏览器请求容易超时
- 后端 worker 被长时间占用，吞吐下降
- 用户体验差（一直转圈）

所以系统把它设计成“批次异步任务 + 进度查询”，让用户体验更稳定、服务更可控。

### 6.2 为什么要有 service 层？

你会发现后端路由文件不应该写太多业务：

- 路由只负责：校验参数、调用 service、返回结果
- service 才负责：业务逻辑、调用 AI、落库

这样做的好处：

- 逻辑可复用（同一业务可被多个 API 调用）
- 更容易测试（后面你会学如何给 service 写测试）
- 文件职责清晰（面试时你能讲出分层思路）

---

## 7. 今日作业（必须完成）

1) 写一段 30 秒项目介绍（照着讲就行）：

- “这是一个 AI 用例生成平台，上传 PRD 后解析文本，结合知识库做 RAG，异步批次生成测试点/用例并落库，前端轮询展示进度，可导出 Excel。”

2) 画一张你自己的“闭环图”（手绘也行）：

```text
前端按钮 → POST /ai/... → 返回 batchId
                     ↓
            后台任务：解析→检索→LLM→落库→更新 batch
                     ↓
前端轮询 GET /ai/batches/{id} → 完成后刷新列表
```

3) 找到并打开这些文件，至少读 5 分钟：

- `backend/app/main.py`
- `backend/app/api/v1/router.py`
- `backend/app/api/v1/ai_operations.py`
- `frontend/src/api/index.ts`
- `frontend/src/components/AiProgressModal.vue`

明天我们会从“配置与数据库”开始，把后端的骨架彻底看懂。
