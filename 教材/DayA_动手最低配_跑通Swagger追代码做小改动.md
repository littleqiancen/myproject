# Day A：动手最低配（跑通 + Swagger 点接口 + 追到代码 + 做一个小改动）

适用人群：编程小白，但想把这个项目变成“面试能讲、被追问不虚”的作品。

你不需要从 0-1 重写整个项目；你只需要完成 4 件事：

1) 跑通前后端
2) 用 Swagger 点 2 个接口
3) 从浏览器按钮追到后端路由函数
4) 做一个小改动（推荐：批次进度字段）并能自测

完成后你就能：

- 说清楚“前端按钮 → 请求哪个 API → 后端哪个函数处理 → 数据存在哪”
- 面试官让你改一个小功能，你不会崩

---

## 0. 你今天会用到哪些文件（先把地图贴出来）

### 0.1 运行说明

- 项目说明：`README.md`（根目录）

### 0.2 后端关键文件

- 后端入口：`backend/app/main.py`
- 路由汇总：`backend/app/api/v1/router.py`
- AI/批次/设置路由：`backend/app/api/v1/ai_operations.py`
- 配置读取：`backend/app/config.py`
- 数据库连接：`backend/app/database.py`
- 批次表模型：`backend/app/models/generation_batch.py`
- API 响应模型：`backend/app/schemas/__init__.py`（`BatchStatusResponse`）

### 0.3 前端关键文件

- API 封装：`frontend/src/api/index.ts`
- 进度弹窗：`frontend/src/components/AiProgressModal.vue`

你今天的“追代码”会从前端按钮开始，最终定位到 `ai_operations.py`。

---

## 1. 必做 1：跑通前后端（Windows 小白照抄）

目标：你能打开：

- `http://localhost:8000/docs`（后端 Swagger）
- `http://localhost:5173`（前端页面）

### 1.1 启动后端

打开 PowerShell，切到项目根目录（你应该能看到 `backend/`、`frontend/` 文件夹）。

进入后端目录：

```powershell
cd .\backend
```

创建虚拟环境（只做一次）：

```powershell
python -m venv venv
```

激活虚拟环境：

```powershell
venv\Scripts\activate
```

安装依赖（只要第一次或依赖更新才需要）：

```powershell
pip install -r requirements.txt
```

启动后端：

```powershell
uvicorn app.main:app --reload --port 8000
```

你应该看到类似：

```text
Uvicorn running on http://127.0.0.1:8000
```

验证后端：

- 打开 `http://localhost:8000/health`，应该返回 `{"status":"ok"}`
- 打开 `http://localhost:8000/docs`，应该看到 Swagger 页面

#### 为什么要先看 `/health` 和 `/docs`

- `/health` 是最小验证：不依赖前端、不依赖 AI
- `/docs` 能看到所有 API，后面追代码你会用它当“地图”

### 1.2 启动前端

再开一个 PowerShell 窗口（保留后端在跑），切到前端目录：

```powershell
cd .\frontend
```

安装依赖（第一次需要）：

```powershell
npm install
```

启动：

```powershell
npm run dev
```

你应该看到类似：

```text
Local:   http://localhost:5173/
```

打开 `http://localhost:5173`，确认页面能打开。

#### 如果页面打开但接口报错怎么办

先不要猜，按顺序验证：

1) 后端 `http://localhost:8000/docs` 能不能打开
2) 浏览器 F12 → Network，看看请求是否打到 `/api/v1/...`
3) 检查前端 `frontend/src/api/index.ts` 的 baseURL 是否是 `/api/v1`

---

## 2. 必做 2：Swagger 点 2 个接口（GET/POST /projects）

目标：你能用后端自带的交互文档，证明“后端真的在工作”。

### 2.1 打开 Swagger

打开：`http://localhost:8000/docs`

### 2.2 点 `GET /projects`

操作：

1) 找到 `GET /projects`
2) 点 `Try it out`
3) 点 `Execute`

你会看到：

- Request URL（请求地址）
- Response body（返回 JSON）

### 2.3 点 `POST /projects`

操作：

1) 找到 `POST /projects`
2) 点 `Try it out`
3) 在请求体里填一个项目名（按接口要求填）
4) 点 `Execute`

你应该看到：

- 返回里带项目 `id` 或项目对象

再回到 `GET /projects`，你应该能看到刚创建的项目。

#### 为什么一定要点这两个接口

- 这是“最小 CRUD”验证：创建 + 列表
- 后面你追 AI 接口时，就能用同样方法验证

---

## 3. 必做 3：从按钮追到代码（第一次“定位路由函数”）

目标：你要做到这件事：

> 我点了一个按钮，我知道它请求了哪个 URL，我能在后端找到处理它的函数。

### 3.1 先在页面点一次 AI 按钮

在前端页面里进入一个项目详情，找到类似：

- “AI 提取测试点”

点一下（如果你没有 Key，可能会失败，但没关系，我们要的是“看到请求路径”）。

### 3.2 在浏览器里看网络请求（Network）

1) 按 `F12`
2) 切到 `Network`
3) 在列表里找到最新的一条请求

你要找的是：

- Request URL（例如：`/api/v1/projects/<id>/ai/extract-test-points`）
- Request Method（例如：`POST`）

把 URL 里最有特点的一段记下来，例如：

- `extract-test-points`

### 3.3 用 IDE 全局搜索定位后端路由

在 IDE 全局搜索（Ctrl+Shift+F）输入你刚才记下的关键词：

- `extract-test-points`

你应该能搜到文件：

- `backend/app/api/v1/ai_operations.py`

打开它，你会看到类似：

- `@router.post("/projects/{project_id}/ai/extract-test-points" ...)`

这就是“后端处理这个按钮请求的入口函数”。

#### 为什么这样追代码最有效

- UI 上的按钮名字可能改
- 但 API 路径一般稳定
- 你用 Network 把路径拿到手，就能稳定定位

---

## 4. 加分 1：做一个小改动（推荐：批次进度字段）

目标：你做一次“后端模型 + API 响应 + 前端展示”的最小闭环改动。

这个改动特别适合面试讲，因为它体现了：

- 异步任务怎么做可观测
- 前后端如何协作
- 数据库字段如何影响 API 返回

### 4.1 你要改哪些文件（按顺序）

1) `backend/app/models/generation_batch.py`（新增进度字段）
2) `backend/app/schemas/__init__.py`（让 API 响应包含进度字段）
3) `backend/app/services/ai/test_case_generator.py`（生成用例时更新进度，最直观）
4) `frontend/src/components/AiProgressModal.vue`（展示进度）

你不想一次改太多的话，也可以先做前 1+2 步，只让后端把字段返回出来。

### 4.2 第一步：给批次表加 2 个字段

文件：`backend/app/models/generation_batch.py`

在 `GenerationBatch` 类里新增：

- `progress_current: int`
- `progress_total: int`

示例（你可以照着写，字段放类里即可）：

```python
progress_current: Mapped[int] = mapped_column(default=0, nullable=False)
progress_total: Mapped[int] = mapped_column(default=0, nullable=False)
```

#### 为什么要加在 model 里

- model 是数据库表结构
- 你不加字段，就没有地方存进度

### 4.3 第二步：让接口响应返回这两个字段

文件：`backend/app/schemas/__init__.py`

找到：

```python
class BatchStatusResponse(BaseModel):
```

新增：

```python
progress_current: int = 0
progress_total: int = 0
```

#### 为什么必须改 schema

这个项目的 `response_model=BatchStatusResponse` 会过滤输出。

- 你不加字段 → 就算数据库里有，也不会返回给前端

### 4.4 第三步：在生成用例时更新进度（最容易看效果）

文件：`backend/app/services/ai/test_case_generator.py`

思路（不用你一次写对所有细节）：

1) 开始生成前：

- `progress_total = 测试点数量`
- `progress_current = 0`

2) 每生成完一个测试点的用例：

- `progress_current += 1`
- `commit` 保存

你要记住一句话：

> 进度不是“算出来”的，是“你每完成一步就写一次”。

### 4.5 第四步：前端展示

文件：`frontend/src/components/AiProgressModal.vue`

你要做的事：

1) 轮询拿到 batch 数据
2) 如果 `progress_total > 0`，就显示：

- `已完成 progress_current/progress_total`
- 百分比 `progress_current / progress_total`

3) 如果 total=0，就显示“处理中”（避免除零）

---

## 5. 自测（必须做，不然你不知道自己改没改对）

### 5.1 后端自测（用 Swagger）

1) 触发一次 AI 生成，拿到 `batch_id`
2) 在 Swagger 调 `GET /ai/batches/{batch_id}`
3) 看返回 JSON 里有没有：

- `progress_current`
- `progress_total`

如果没有：

- 八成是你没改 `BatchStatusResponse`

### 5.2 前端自测

打开进度弹窗，看它是否显示“已完成 x/y”。

---

## 6. 你要能讲清楚“为什么这样写”（面试话术模板）

你按这个模板讲就行：

1) 背景：AI 生成是异步任务，用户需要知道进度
2) 方案：批次表增加 `current/total`，任务执行中持续更新
3) 接口：批次查询接口返回进度字段
4) 前端：轮询展示进度，避免除零
5) 扩展：规模更大时可以用任务队列 + SSE/WebSocket

---

## 7. 今日最小交付（你只要做到这些就算完成）

必做：

- 能打开 `http://localhost:8000/docs` 和 `http://localhost:5173`
- Swagger 点过 `GET /projects`、`POST /projects`
- 用 F12 Network 拿到一个 `/api/v1/...` 路径，并在后端找到对应 `@router...` 函数

加分（推荐）：

- 批次进度字段能在 `GET /ai/batches/{id}` 返回
- 前端进度弹窗能显示 `x/y`

