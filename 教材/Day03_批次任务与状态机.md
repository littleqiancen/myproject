# Day 3：批次任务与状态机（面试最加分的工程点）

目标：你要能讲清楚“为什么用批次任务、状态怎么设计、前端怎么拿进度、失败怎么办”。

---

## 1. 小白先懂：什么是“批次任务（Batch）”

你可以把它类比成“外卖订单”：

- 你点单（发起生成）
- 商家开始做（后台异步跑）
- 你随时看进度（轮询订单状态）
- 做完送到（生成完成，刷新列表）

这里的“订单号”就是 `batch_id`。

如果你只能记一句话：

> 批次任务 = “把慢操作从 HTTP 请求里剥离出来”，让用户先拿到一个可查询的编号。

---

## 2. 为什么 AI 生成一定要异步

因为 AI 生成通常满足 3 个特征：

1) 耗时长（几十秒到几分钟）
2) 不确定（LLM 可能失败、超时、限流）
3) 需要可观测（用户想知道进度/失败原因）

如果你用同步接口一次性返回结果：

- 浏览器/网关/负载均衡可能超时
- 后端 worker 被卡住，其他请求受影响
- 用户只看到“转圈/失败”，不知道发生了什么

所以设计成：

> 同步返回 `batch_id` + 后台执行 + 进度查询。

---

## 3. 代码应该从哪里读

你今天要精读 3 个文件：

1) 批次模型：`backend/app/models/generation_batch.py`
2) AI 路由：`backend/app/api/v1/ai_operations.py`
3) 前端进度轮询：`frontend/src/components/AiProgressModal.vue`

### 3.1 手把手阅读法：不要“看”，要“跟”

你按这个顺序做（每一步都能得到一个确定答案）：

1) 打开前端页面，点击一次“AI 提取测试点”
2) 打开浏览器 F12 → Network
3) 找到请求 URL，例如 `/api/v1/projects/1/ai/extract-test-points`
4) 在 IDE 全局搜索 `extract-test-points`
5) 跳转到后端对应的路由函数
6) 在这个路由函数里找：
   - batch 是怎么创建的
   - 后台任务函数叫什么
   - batchId 是怎么返回给前端的
7) 打开 `AiProgressModal.vue`，找：
   - 它多久轮询一次
   - 轮询的接口 URL 是什么
   - 收到 succeeded/failed 后做了什么

你做完一次，你就知道“批次系统”的骨架了。

---

## 4. 批次状态机怎么设计（你要会讲“设计思路”）

### 4.1 最小状态集

最常见的状态：

- `pending`：已创建但未开始
- `running`：执行中
- `succeeded`：成功
- `failed`：失败

为什么这 4 个足够？

- 用户视角只关心：有没有开始、还在不在跑、最终成没成
- 工程视角需要：失败可追溯（记录 error）

### 4.2 可选的增强状态（进阶）

如果你想做得更工程化：

- `canceled`：用户取消
- `retrying`：重试中
- `partial_succeeded`：部分成功（例如 N 个测试点生成了 M 个）

什么时候需要这些？

- 任务量大、重试策略复杂
- 你希望 UI 更精细的体验

### 4.3 状态应该记录哪些字段

建议字段（不一定全有，按项目实际为准）：

- `status`
- `created_at/updated_at`
- `error_message`（失败原因）
- `progress_current/progress_total`（可选，进度）

为什么要 `progress_total`？

- UI 才能显示“完成了多少/还剩多少”
- 你才能做“估算剩余时间”的能力

#### 手把手：在本项目里 batch 状态是怎么落库的？

1) 打开 `backend/app/models/generation_batch.py`
2) 找到字段：

- `status`
- `error_message`（如果有）
- `created_at/updated_at`（如果有）

3) 在 `backend/app/api/v1/ai_operations.py` 搜索 `GenerationBatch`，看看创建时默认是什么状态

4) 在 `backend/app/services/ai/test_point_extractor.py` / `test_case_generator.py` 搜索 `batch` 或 `status`，看看什么时候改 running/succeeded/failed

你只要能把这 4 步做出来，就不是“空理解”。

---

## 5. 后端接口的典型实现方式（你要学会看“套路”）

### 5.1 创建批次并返回

在 `ai_operations.py` 里你会看到类似模式：

1) 校验参数（project_id、是否有文档、是否配置模型等）
2) 创建 `GenerationBatch`（状态设为 pending）
3) 立刻返回 `batch_id`
4) 启动后台任务（`asyncio.create_task(...)`）

为什么“先返回，再执行”？

- 避免 HTTP 超时
- UI 能立即响应

#### 新手必懂：`asyncio.create_task` 是什么

你可能会看到类似：

- `asyncio.create_task(do_work(...))`

它的意思是：

- **不要等待** `do_work` 执行完
- 让它在后台继续跑
- 当前请求立刻返回

这就是“异步批次”的关键。

### 5.2 后台任务更新状态

后台任务（例如 `test_point_extractor.py`）通常做：

- 开始：把 batch 改成 running
- 成功：把 batch 改成 succeeded
- 失败：把 batch 改成 failed 并记录 error

你要能回答面试官：

> “批次状态是落库的，所以即使前端刷新，仍然能查到生成进度与失败原因。”

---

## 6. 前端为什么用“轮询”

最常见的 3 种方案：

1) 轮询（Polling）：每隔 N 秒请求一次状态
2) WebSocket：后端主动推送进度
3) SSE：服务端推送事件流

项目选择轮询的原因（新手版）：

- 实现简单、稳定
- 不需要维护长连接
- 对后端/网关要求低

缺点：

- 有额外请求开销
- 时间粒度受间隔影响

你可以在 `AiProgressModal.vue` 看到它每 2 秒查询一次批次状态。

面试加分点：

> “如果任务量更大，我会考虑 SSE/WebSocket，并做后端限流与合并更新。”

---

## 7. 从 0 开始写一个最小“批次任务系统”（你照抄就能跑）

这一节非常重要：你会亲手写出一个“创建任务 → 查状态”的最小版本。

### 7.1 需求（极简版）

- `POST /jobs`：创建一个任务，返回 `job_id`
- `GET /jobs/{job_id}`：查询任务状态
- 后台任务：睡 5 秒后完成（模拟慢操作）

### 7.2 数据结构（你先不用数据库，先用内存字典）

```python
jobs = {
  "job_id": {"status": "running", "error": None}
}
```

### 7.3 代码（完整可运行）

```python
import asyncio
import uuid
from fastapi import FastAPI

app = FastAPI()

jobs: dict[str, dict] = {}


async def do_work(job_id: str):
    try:
        jobs[job_id]["status"] = "running"
        await asyncio.sleep(5)
        jobs[job_id]["status"] = "succeeded"
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)


@app.post("/jobs")
async def create_job():
    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "pending", "error": None}
    asyncio.create_task(do_work(job_id))
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    return jobs.get(job_id, {"status": "not_found"})
```

你把它存成 `mini_jobs.py`，运行：

```bash
uvicorn mini_jobs:app --reload --port 8003
```

然后：

1) `POST http://localhost:8003/jobs` 拿到 job_id
2) 每隔 1 秒 `GET http://localhost:8003/jobs/{job_id}` 看状态

你一旦跑通这个最小例子，就能完全理解本项目的批次机制只是把“内存字典”升级成了“数据库表”，把“sleep 5 秒”升级成了“AI 生成”。

---

## 7. 从 0-1 你该怎么写这一套（非常关键）

如果你要自己从零写“批次异步任务”，我建议按下面顺序：

### 7.1 先写批次表

- 先有“持久化的状态”才能做可观测

### 7.2 再写创建批次的 API

- `POST /jobs` 返回 `job_id`

### 7.3 再写查询状态的 API

- `GET /jobs/{id}` 返回 status/error/progress

### 7.4 最后才写后台任务

- 任务开始/结束要更新 job 状态

为什么是这个顺序？

- 先让系统“可用、可观察、可调试”
- 再把复杂的 AI 逻辑塞进去

---

## 8. 今日操作练习（必须做）

1) 把你跑通的链路用文字写下来（10 行以内）：

- 点哪个按钮 → 调哪个接口 → 返回什么 → 前端怎么显示

2) 读代码时做 2 个标注：

- `batch` 在哪个地方创建？（文件+函数）
- `batch` 在哪个地方更新状态？（文件+函数）

3) 练习面试回答（建议录音 1 分钟）：

> “为什么你们不用同步生成？”

4) 额外练习（推荐）：

- 把上面的 `mini_jobs.py` 跑起来（你会对批次系统理解暴涨）

明天我们进入“LLM 调用与 Prompt 工程”，这是 AI 系统质量的核心（Day 4）。
