# Day 2：配置与数据库基础（你必须掌握的后端骨架）

目标：你要能解释“数据存哪里、配置从哪来、为什么这么分层”，并能从 0-1 搭一个最小 FastAPI + SQLite 异步项目。

---

## 1. 先建立 3 个关键概念（小白版）

### 1.1 什么是“配置”

配置就是：程序运行时会变、但代码不想改的东西。

典型配置：

- 端口号
- 数据库路径
- LLM API Key
- 模型名称
- 向量库路径

为什么不能写死在代码里？

- 安全：Key 不能写进仓库
- 灵活：开发/测试/生产环境不一样
- 可运维：上线后改配置不需要改代码

### 1.2 什么是 ORM（SQLAlchemy）

ORM 就是把“数据库表”映射成“Python 类”。

你用类和对象写数据，不直接手写 SQL。

优点：

- 更容易维护（字段改动更集中）
- 业务逻辑更贴近代码表达
- 复杂查询也能表达（当然也可以写原生 SQL）

### 1.3 为什么要用异步（async）

这个系统最耗时的是：

- 外部调用（LLM API）
- 文件解析
- 向量检索

用 async 能更好地利用等待时间，提高并发能力。

---

## 2. 项目里的配置系统怎么设计

你需要重点读：

- `backend/app/config.py`
- 根目录 `.env.example`
- `backend/settings.json`（如果存在或运行时生成）

### 2.1 `.env`/环境变量（Environment Variables）

环境变量是操作系统层面的配置注入方式。

特点：

- 不写进代码
- 部署时由容器/运维系统注入

新手常见误区：

- 把真实 Key 写进 `.env` 并提交（危险）
- 用占位符 `sk-xxx` 当真 Key（运行必失败）

#### 手把手：你现在的项目里 `.env` 在哪里？

在本仓库里，根目录已经有一个 `.env`（你可以打开看）。常见内容类似：

```bash
DATABASE_PATH=casegen.db
DEFAULT_LLM_MODEL=openai/gpt-4o
OPENAI_API_KEY=
```

你要学会判断：

- `OPENAI_API_KEY=` 为空 → AI 相关功能可能无法调用
- 但你依然可以先跑通页面与普通 CRUD 接口

#### 手把手：我到底要不要手动填 `.env`？

对新手最推荐的路径是：

- **先不填 `.env`**
- 先跑通系统
- 再去前端页面的“系统设置”填 Key/模型，保存

原因：

- 你不用理解环境变量就能配置好
- 设置会写入 `backend/settings.json`，重启后还在

### 2.2 `settings.json`：为什么要落盘一份配置

### 2.2 `settings.json`：为什么要落盘一份配置

项目里有“在 UI 上修改配置”的能力：

- 用户在页面填写模型、Key、向量库路径等
- 后端把它保存成 `backend/settings.json`

这样做的原因：

- 对“非开发用户”友好：不用去编辑 `.env`
- 让配置变更可追溯、可恢复

你可以在 `backend/app/config.py` 找到类似逻辑：

- 启动时：先读环境变量，再尝试覆盖/补全为 `settings.json`
- 保存时：对 Key 做脱敏显示（只展示前后几位）

为什么要脱敏？

- 避免前端回显泄露
- 避免日志输出泄露

#### 手把手：用 UI 保存配置，然后确认后端真的读到了

你按下面步骤做一次“验证”，就能真正理解配置系统：

1) 确保前后端都启动

2) 打开前端：`http://localhost:5173` → 进入“系统设置”页

3) 填写：

- 模型：例如 `openai/gpt-4o`（只要跟项目支持的格式一致即可）
- Key：填你自己的 Key（不要提交到仓库）

4) 点保存

5) 回到代码目录，找到 `backend/settings.json`

你应该看到它出现，并且里面是你刚刚保存的字段。

6) 打开后端 Swagger：`http://localhost:8000/docs`

7) 调用 `GET /settings`

你应该看到：

- Key 被脱敏（只显示一部分）
- 说明后端确实读到了 settings

这一步非常关键：你以后遇到“我填了 Key 但不生效”，就能定位是“没保存到文件”还是“后端没读取”。

---

## 3. 数据库怎么设计：从“表”到“模型”

你要找到并理解：

- `backend/app/database.py`：创建异步 engine、session
- `backend/app/models/`：ORM 模型（表结构）

### 3.1 SQLite 在这里扮演什么角色

SQLite 是“单文件数据库”。

优点：

- 零运维：不用装 MySQL/Postgres
- 本地开发非常方便

缺点：

- 并发写能力一般
- 多机部署要考虑共享存储

为什么项目选 SQLite？

- 这是一个工具平台/原型产品，优先让系统能跑起来
- 后续需要高并发/生产化时可以换 Postgres

### 3.2 手把手：找到数据库文件在哪

你先记住一句话：

> SQLite 的数据库就是一个文件，文件在哪，数据就在哪。

在根目录 `.env` 里有：

```bash
DATABASE_PATH=casegen.db
```

这意味着：

- 如果你在 `backend/` 目录启动后端，那么 DB 文件通常出现在 `backend/casegen.db`
- 如果你在根目录启动后端，那么 DB 文件可能出现在根目录

新手最容易在这里迷路，所以你要用“事实”验证：

1) 启动后端
2) 去 `backend/` 和根目录分别看看有没有 `casegen.db`

### 3.3 手把手：用 Python 直接查看数据库里有哪些表

你不需要安装额外工具，用 Python 就能看。

在 `backend/` 目录，执行：

```powershell
python -c "import sqlite3; c=sqlite3.connect('casegen.db'); print(c.execute('select name from sqlite_master where type=\"table\"').fetchall())"
```

你应该看到一串表名，例如 `projects`、`documents`、`test_points`、`test_cases`、`generation_batches`（以实际为准）。

如果你看到空列表 `[]`：

- 说明你看的这个 `casegen.db` 不是正在使用的那个（路径不对）
- 或者后端还没启动过（没建表）

---

## 4. 你必须理解的“分层”到底是什么（别背概念，按职责记）

后端常见分层（这项目也基本符合）：

- `api/`：HTTP 层（接收请求、参数校验、返回 JSON）
- `services/`：业务层（真正处理“生成测试点/生成用例/知识库入库”等）
- `models/`：数据层（数据库表结构）
- `schemas/`：数据协议层（API 返回/入参的结构）

你记住一句话就行：

> 路由文件不要写大段业务逻辑，大段业务逻辑放 service；表结构放 model。

为什么这样做？

- 方便复用：同一个 service 逻辑可以被多个 API 调用
- 方便测试：你可以直接测试 service，不必起 HTTP
- 方便维护：改动影响范围小

### 3.2 你必须理解的 4 张核心表（建议按这个顺序看模型）

1) `Project`：一个业务项目

- 关联上传的文档
- 关联测试点、测试用例

2) `GenerationBatch`：一次 AI 生成批次

- 状态：pending/running/succeeded/failed（具体以代码为准）
- 错误信息、时间戳

3) `TestPoint`：测试点

- AI 从 PRD 提取的“要测什么”

4) `TestCase`：测试用例

- 基于测试点生成的“怎么测”

你可以把它理解成：

> Project 是容器；TestPoint/TestCase 是内容；GenerationBatch 是“生成过程的状态记录”。

---

## 4. 从 0-1 如何写这一套后端骨架（最小可运行版）

下面是“从空项目开始”的建议顺序（非常重要）：

### 4.1 第一步：先搭 FastAPI 入口

创建 `app/main.py`：

- 创建 `FastAPI()`
- 写一个 `/health` 接口（最小验证）
- `uvicorn` 启动

为什么先写 `/health`？

- 它不依赖数据库、不依赖 AI
- 能最快验证服务正常

#### 手把手：你在本项目里能找到 `/health` 吗？

打开：`backend/app/main.py`

你会看到：

- `@app.get("/health")`

你现在就能理解：

- 这个接口是“服务是否活着”的最小验证

### 4.2 第二步：加配置层（config）

创建 `app/config.py`：

- 读环境变量（例如 DB 路径、模型 Key）
- 允许默认值（新手最容易卡在“没配 Key 直接崩”）

为什么要有默认值？

- 能让系统先跑起来
- 关键配置（Key）再通过 UI 或 env 补齐

### 4.3 第三步：加数据库层（database）

创建 `app/database.py`：

- 创建 async engine
- 创建 async sessionmaker
- 提供 `get_db()` 依赖（FastAPI 依赖注入）

为什么要用依赖注入？

- 每个请求有自己的 session 生命周期
- 易于测试（可以注入 mock session）

#### 手把手：你在本项目里怎么找到 `engine/session`？

打开：`backend/app/database.py`

你重点看两件事：

1) `create_async_engine(...)`
2) `async_sessionmaker(...)`

这两样就是“怎么连上 SQLite”与“怎么创建数据库会话”。

---

## 5. 从 0 开始写代码：一个最小 CRUD + SQLite（你照抄就能跑）

这部分是“手把手写代码”的核心。你可以在自己电脑任意目录新建一个文件夹跟着做。

### 5.1 新建目录结构（最小版）

```text
mini_backend/
  app/
    __init__.py
    main.py
    config.py
    database.py
    models.py
```

### 5.2 `config.py`（读取 `.env`）

```python
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_PATH: str = "mini.db"
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


def get_settings() -> Settings:
    return Settings()
```

### 5.3 `database.py`（创建异步引擎与会话）

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .config import get_settings

settings = get_settings()

engine = create_async_engine(
    f"sqlite+aiosqlite:///{settings.DATABASE_PATH}",
    echo=False,
)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
```

### 5.4 `models.py`（一张表：Project）

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str]
```

### 5.5 `main.py`（建表 + 2 个接口）

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import engine, get_db
from .models import Base, Project


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/projects")
async def create_project(name: str, db: AsyncSession = Depends(get_db)):
    p = Project(name=name)
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return {"id": p.id, "name": p.name}


@app.get("/projects")
async def list_projects(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Project))).scalars().all()
    return [{"id": p.id, "name": p.name} for p in rows]
```

### 5.6 启动并验证

在 `mini_backend/` 目录：

```bash
pip install fastapi uvicorn sqlalchemy aiosqlite pydantic-settings
uvicorn app.main:app --reload --port 8002
```

打开：`http://localhost:8002/docs`，用 Swagger 先创建再查询。

你一旦把这个 mini 版本跑通，再回来看本项目，你会突然发现“原来只是多了很多业务文件”，骨架是一致的。


### 4.4 第四步：写模型（models）

创建 `app/models/project.py`、`generation_batch.py` 等。

原则：

- 模型只表达表结构，不写业务逻辑
- 复杂业务放 service

### 4.5 第五步：写路由聚合（api/v1）

创建 `app/api/v1/router.py`：

- 把 `projects`、`ai_operations` 等路由 include 进去
- 统一前缀 `/api/v1`

为什么要统一前缀？

- 版本管理（v1/v2）
- 反向代理、权限控制更方便

---

## 5. 今日操作练习（必须做）

1) 打开并精读（至少 20 分钟）：

- `backend/app/config.py`
- `backend/app/database.py`

2) 画一张“配置读取优先级”图（你写到笔记里就行）：

```text
环境变量 .env → config.py 解析 → settings.json（UI 保存）覆盖/补全 → 应用内读取配置
```

3) 找出数据库文件实际落在哪里：

- 在 `config.py` 找 `DATABASE_PATH` 默认值
- 在 Docker 配置里找 volume 映射（`docker-compose.yml`）

你要能回答面试官：

> “这个项目的数据是存 SQLite 文件的，部署时通过 volume 持久化。”

明天我们进入全项目最关键的工程设计：批次异步任务与前端轮询（Day 3）。
