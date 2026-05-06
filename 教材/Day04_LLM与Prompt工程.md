# Day 4：LLM 调用与 Prompt 工程（让 AI 结果可控）

目标：你要能解释“为什么要封装 LLM 客户端、Prompt 怎么组织、结构化 JSON 怎么保证、失败怎么处理”。

---

## 1. 小白先懂：AI 接口调用有什么坑

LLM 调用和普通 API 最大区别：

- 输出不稳定：同样输入可能返回不同格式
- 容易超时/限流：第三方服务不受你控制
- 会胡说（幻觉）：必须用工程方法约束

所以你必须学会：

> 把“不可控的自然语言输出”变成“可验证的结构化输出”。

补一句更工程化的：

> 你要把 LLM 当成一个“不可靠的外部依赖”，用校验、重试、降级把它变可靠。

---

## 2. 本项目的 LLM 封装怎么读

你重点读 2 个文件：

- `backend/app/services/ai/llm_client.py`
- `backend/app/services/ai/prompts.py`

### 2.0 手把手：先让你“看到”模型配置在哪里

你先打开根目录 `.env`，你会看到这些字段（可能为空）：

- `DEFAULT_LLM_MODEL`
- `OPENAI_API_KEY`
- `LLM_API_BASE`

然后打开：`backend/app/config.py`

你会看到默认值与读取顺序：

1) 先读 `.env` / 环境变量
2) 再用 `backend/settings.json` 覆盖（UI 保存的设置优先）

对新手来说：

- **优先用 UI 配置**（最省事）
- `.env` 作为你学会后再用的方式

### 2.1 为什么要封装 `llm_client`

如果你在业务代码里到处写：

- model 名称
- API key 读取
- timeout/retry
- provider 差异

会发生什么？

- 改模型要改一堆文件
- 线上问题难定位
- 难以做统一的重试/日志/限流

所以封装的目标是：

- 一个统一入口：`generate(...)`
- 业务只关心“我要什么输出”，不关心“怎么连模型”

#### 手把手：你怎么在代码里找到“实际请求模型的那一行”

做法（你现在就能做）：

1) 打开 `backend/app/services/ai/llm_client.py`
2) 全局搜索关键字：

- `completion`
- `litellm`
- `messages`

3) 你会找到一个“把 messages 发给模型”的函数

你只要定位到这行，就等于知道“LLM 在哪里被调用”。

### 2.2 Prompt 为什么集中在 `prompts.py`

Prompt 本质上是“业务规则的一部分”。

集中管理的好处：

- 版本可控（你可以对比 prompt 改动对结果的影响）
- 易复用（测试点/用例生成可以复用同一段模板）
- 易调优（统一加 system message、统一约束输出格式）

---

## 3. 结构化输出：为什么一定要 JSON

生成测试点/用例，如果让模型自由发挥：

- 前端无法稳定展示
- 后端无法稳定落库
- 你无法写自动化测试

所以必须要求模型输出 JSON。

### 3.1 你需要做的 3 层约束

1) Prompt 约束：

- 明确要求“只输出 JSON，不要多余文字”
- 提供 JSON 示例

2) 解析约束：

- 后端必须做 JSON parse
- parse 失败要重试或报错

3) Schema 约束（更工程化）：

- 用 Pydantic/JSON Schema 校验字段
- 不合格就判失败或触发重试

你可以在 `test_point_extractor.py`、`test_case_generator.py` 看到解析与落库逻辑。

---

## 3.2 手把手：用一个最小例子体验“让模型只输出 JSON”

你先不接入真实 LLM，先用一个“假模型返回”练习解析。

### 3.2.1 你要的目标输出

我们假设模型返回测试点列表：

```json
{
  "test_points": [
    {"title": "登录失败", "priority": "P0"}
  ]
}
```

### 3.2.2 解析器（你照抄）

```python
import json
import re


def extract_json(text: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


raw = "这里是多余文字\n{\"test_points\":[{\"title\":\"登录失败\",\"priority\":\"P0\"}]}"
data = extract_json(raw)
print(data["test_points"][0]["title"])
```

你会看到输出 `登录失败`。

这个练习的意义：

- 你知道“模型可能会夹杂解释文字”
- 你知道“后端必须把 JSON 摘出来再 parse”

后面你再看本项目的解析代码，就不会觉得神秘。

---

## 4. 为什么要把 AI 逻辑放在 service 层

对小白来说，路由里直接写 AI 逻辑“也能跑”，但长期会很痛。

正确分层：

- `api/v1/*.py`：只做 HTTP 层（校验/返回）
- `services/ai/*.py`：负责 AI 业务（prompt、调用、解析、落库）

这样设计的原因：

- 你可以单独测试 service（不启动 HTTP）
- 你可以复用 service（例如定时任务/后台脚本也能调用）
- 你的路由文件不会变成 1000 行

---

## 5. 从 0-1 写 LLM 调用（你照着写就能复刻）

下面是推荐顺序：

### 5.1 先定义“你要的输出结构”

例如测试点：

- `title`
- `description`
- `priority`

你先把它变成一个 Pydantic 模型（或至少定义 dict 的字段）。

为什么先定义输出？

- 你才能写 prompt
- 你才能落库
- 你才能验证

#### 手把手：输出结构怎么跟数据库字段对齐

你要记住顺序：

1) 先决定你要展示什么（UI 需要哪些字段）
2) 再决定你要存什么（DB 字段）
3) 最后让模型按这个结构输出（Prompt + Schema 校验）

这就是“工程先于 AI”的思路。

### 5.2 写 Prompt 模板

Prompt 模板包含：

- 角色：你是谁（系统/助手）
- 任务：你要做什么（提取测试点/生成用例）
- 输入：给它 PRD 内容、给它 RAG 片段
- 输出：严格 JSON + 示例

### 5.3 写统一 LLM Client

最小接口：

- 入参：`model`, `messages`, `temperature`, `timeout`
- 出参：字符串（原始） + token 统计（可选）

### 5.4 写“解析 + 校验”

流程：

1) 找到 JSON（去掉可能的多余文字）
2) `json.loads`
3) 校验字段
4) 返回结构化对象

### 5.5 失败策略（面试加分）

你至少准备 3 个策略：

- 解析失败：再问一次并提示“只输出 JSON”
- 限流/超时：指数退避重试
- 结果不完整：提示补齐缺失字段

#### 新手常见问题：我没有 Key，怎么学这一章？

你完全可以先学会“框架与套路”，再补 Key。

建议顺序：

1) 先跑通系统的 CRUD 与页面
2) 用 UI 配置 Key（不会写 `.env` 也行）
3) 再实际触发一次 AI 生成

---

## 6. 从 0 开始：写一个最小“LLM 客户端封装”（带 mock）

新手最容易卡在“没有 Key / 不想花钱”。所以我教你先用 mock。

### 6.1 目标

- 业务代码永远调用 `llm_generate(prompt)`
- 本地没配置 Key 时，返回一个固定 JSON（mock）
- 配置 Key 后，才走真实模型

### 6.2 伪代码示例

```python
import os


def llm_generate(prompt: str) -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        return '{"test_points":[{"title":"mock 测试点","priority":"P1"}]}'

    # 这里再去调用真实模型（你学会后再接）
    raise NotImplementedError
```

这段的意义：

- 让你先把“解析/落库/展示”链路打通
- AI 只是可插拔依赖，不会阻塞你学习

---

## 6. 今日操作练习（必须做）

1) 打开并通读：

- `backend/app/services/ai/llm_client.py`
- `backend/app/services/ai/prompts.py`

2) 找出“测试点提取”调用 LLM 的那一行（文件+函数），写到笔记里。

3) 练习回答（1 分钟）：

> “你怎么保证 AI 生成的用例格式稳定、能落库？”

4) 额外练习（推荐）：

- 在 `test_point_extractor.py` 搜索 `json`，找出“解析 JSON 的位置”，并写下它失败会发生什么。

明天我们学 RAG 与知识库：如何让 AI 有“外部记忆”，提高准确率（Day 5）。
