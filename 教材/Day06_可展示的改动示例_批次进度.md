# Day 6：可展示的改动示例——给批次任务加“进度”（面试杀手锏）

目标：学会在“前后端分离 + 异步批次任务”的架构里做一次完整的小需求：

- 改数据库模型
- 改后端 service 更新进度
- 改后端 API 返回进度
- 改前端 UI 展示进度
- 自测并准备面试讲法

注意：本教程是“教你如何写”，不强制你今天就把代码提交。你也可以跟着做一遍并保留为自己的作品改动。

---

## 1. 为什么我推荐这个改动

因为它非常面试友好：

- 有完整闭环（DB → API → UI）
- 改动不大但能体现工程思维
- 能自然引出：状态机、幂等、失败处理、观测性

而且它正好补强了“异步任务”的用户体验：

- 现在用户只知道“在跑”，不知道“跑到哪”
- 有进度后用户更安心，也方便定位卡点

---

## 1.1 新手写代码的正确姿势（避免你越改越乱）

你按这 6 步做，几乎不会翻车：

1) **先跑通**：确保你现在能正常生成一次测试点/用例
2) **再备份 DB**：把 `casegen.db` 复制一份（怕改坏）
3) **再小步改动**：一次只改一个文件，跑一次
4) **每次改完就验证**：用 Swagger 或页面验证
5) **遇到报错先回滚**：把改动撤回，找最小差异
6) **最后再做 UI 美化**：先把功能跑通再美化

---

## 2. 先做需求拆解（新手最容易漏这一步）

需求：

> 生成测试点/用例时，前端进度弹窗显示“已完成/总数”和百分比。

拆解为 4 个子任务：

1) 数据层：batch 表需要能存 `current/total`
2) 业务层：后台生成时要不断更新 `current`
3) 接口层：`GET /ai/batches/{id}` 返回进度字段
4) 前端层：弹窗组件展示进度

---

## 3. 你要改哪些文件（按顺序）

先定位这些文件：

- 批次模型：`backend/app/models/generation_batch.py`
- AI 路由：`backend/app/api/v1/ai_operations.py`
- 批次响应模型：`backend/app/schemas/__init__.py`（`BatchStatusResponse`）
- 任务实现：
  - `backend/app/services/ai/test_point_extractor.py`
  - `backend/app/services/ai/test_case_generator.py`
- 前端弹窗：`frontend/src/components/AiProgressModal.vue`

---

## 4. 具体实现步骤（从 0-1 你就按这个做）

### 4.1 第一步：扩展批次模型（数据库字段）

在 `GenerationBatch` 增加字段：

- `progress_current`（int，默认 0）
- `progress_total`（int，默认 0 或 nullable）

#### 4.1.1 手把手：在代码里怎么写（示例 diff）

打开 `backend/app/models/generation_batch.py`，在字段区新增两行（位置随你，只要在类里）：

```diff
 class GenerationBatch(Base, TimestampMixin):
@@
     status: Mapped[str] = mapped_column(String(20), default="running")
     error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
     started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
     completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
+
+    progress_current: Mapped[int] = mapped_column(default=0, nullable=False)
+    progress_total: Mapped[int] = mapped_column(default=0, nullable=False)
```

为什么我这里用 `default=0` 而不是 nullable？

- 对新手更简单：永远是数字，前端不用处理 None
- 百分比计算也更安全（只要避免 total=0 除零）

为什么要有 total？

- 没 total 就只能显示“已完成 X”，无法给百分比

如果你担心兼容性：

- 让 `progress_total` 可为空
- UI 发现为空就只显示“处理中”

SQLite 没有 migrations 怎么办？

- 这个项目启动时可能会自动创建表，但字段新增不一定自动 alter。
- 你可以选择：
  - 开发阶段直接删除本地 sqlite 文件重新生成（最快）
  - 或者手写 `ALTER TABLE`（更像生产化）

#### 4.1.2 新手最快方案：删库重建（只适合本地）

如果你本地数据不重要：

- 停掉后端
- 删除正在使用的 `casegen.db`
- 重启后端（它会自动建表）

如果你不确定 DB 文件在哪：看 Day02 的“找数据库文件在哪”。

面试时你可以说：

> “原型期可以删库重建，生产要用迁移工具（Alembic）管理 schema。”

### 4.2 第二步：在后台任务里更新进度

#### A）提取测试点任务（按阶段更新）

`test_point_extractor.py` 里通常有几个阶段：

1) 读取文档
2) RAG 检索（可选）
3) 调用 LLM
4) 解析 JSON
5) 写入数据库

你可以把它粗略当成 5 步，所以 total=5，然后每完成一步 `current += 1`。

优点：

- 非常简单
- 不需要知道“总共会生成多少测试点”

缺点：

- 进度粒度粗

#### B）生成测试用例任务（按测试点数量更新）

`test_case_generator.py` 往往是“按测试点循环生成”。

这非常适合做精细进度：

- `progress_total = 测试点数量`
- 每生成完一个测试点的用例 `progress_current += 1`

面试官会喜欢这种“可解释、可量化”的进度。

### 4.3 第三步：让批次查询 API 返回进度字段

在 `GET /ai/batches/{id}` 的返回结构里增加：

- `progress_current`
- `progress_total`
- `progress_percent`（可选，后端算好给前端）

#### 4.3.1 手把手：修改 `BatchStatusResponse`

打开 `backend/app/schemas/__init__.py`，找到：

```python
class BatchStatusResponse(BaseModel):
```

新增两个字段：

```diff
 class BatchStatusResponse(BaseModel):
     id: str
     batch_type: str
     status: str
     error_message: str | None = None
     token_usage: dict | None = None
     started_at: datetime | None = None
     completed_at: datetime | None = None
+    progress_current: int = 0
+    progress_total: int = 0
```

为什么要改 response model？

- FastAPI 的 `response_model` 会做输出过滤
- 你不加字段，后端即使查询到也不会返回给前端

为什么建议后端算 percent？

- 统一规则（避免前端/后端口径不一致）
- 后端可以处理 total=0/None

### 4.4 第四步：前端展示

在 `AiProgressModal.vue` 里：

- 轮询拿到批次数据
- 展示：
  - 文本：`已完成 current/total`
  - 进度条：percent

如果 total 不存在：

- 进度条显示 indeterminate（不确定状态）
- 文本显示“处理中”

#### 4.4.1 手把手：前端怎么显示百分比（思路版）

你只需要做 3 件事：

1) 轮询拿到 `progress_current/progress_total`
2) 计算 percent（注意 total=0）
3) 渲染到进度条组件

伪代码：

```ts
const percent = batch.progress_total
  ? Math.round((batch.progress_current / batch.progress_total) * 100)
  : undefined
```

如果 `percent` 是 `undefined`，就展示“不确定进度”。

---

## 5. 自测清单（新手照着点就行）

1) 触发“生成测试用例”
2) 打开进度弹窗
3) 看进度是否递增
4) 任务成功后弹窗关闭/提示成功
5) 刷新用例列表，能看到新数据

常见 bug：

- 后台任务更新进度时 session 没提交（commit）
- 前端轮询频率太快导致压力（2s 一般 OK）
- total=0 导致除零错误

再补 2 个常见坑：

- 你改了 model 但没删库/没迁移 → 运行时可能报“列不存在”
- 前端拿到了字段但没刷新 UI 状态（比如响应没赋值到 reactive 变量）

---

## 6. 面试怎么讲（你直接背这段）

你可以按 5 句结构讲：

1) 痛点：AI 生成是异步任务，用户不知道进度体验差
2) 目标：让用户看到“完成了多少/还剩多少”，并能定位卡点
3) 方案：batch 表新增 current/total，任务执行中持续更新，API 返回进度，前端轮询展示
4) 风险与处理：避免除零、失败保留 error、轮询间隔与限流
5) 扩展：生产化会用任务队列（Celery/RQ）+ 事件推送（SSE/WebSocket）

---

## 7. 今日作业（必须完成）

1) 你在纸上写清楚：

- “提取测试点”进度用阶段式还是按条数？为什么？
- “生成用例” total 用什么算？

2) 你在笔记里列出你要改的 4 个文件路径（见第 3 节）。

3) 你写一段 5 句“改动讲稿”（见第 6 节），录音一遍。

明天（Day 7）我们把项目包装成“面试作品”：演示脚本、讲解稿、常见追问答案。
