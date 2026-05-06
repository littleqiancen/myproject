# Day 0：新手必读——工具与基础概念（先把地基打牢）

目标：你要在 1 天内搞清楚“我在用什么工具、我在运行什么、我遇到报错该怎么查”。

如果你是编程小白，这一篇比 Day1 更重要：它会把后面 7 天所有操作需要的基础知识都补齐。

---

## 1. 你将要做的事情，用一句话描述

你要在自己电脑上运行一个 Web 应用：

- **后端**（Python 程序）在本机 `8000` 端口提供 API
- **前端**（Node 构建的网页）在本机 `5173` 端口提供页面
- 浏览器访问前端页面，前端再请求后端 API

你只要记住 3 个词：

- **端口**：同一台电脑上不同服务的“门牌号”
- **URL**：访问地址（例如 `http://localhost:8000/docs`）
- **API**：前端向后端拿数据/触发功能的接口

---

## 2. 必装软件（建议一次装齐）

你可以用“最低配组合”，不追求花里胡哨：

- Python 3.12+（后端）
- Node.js 18+（前端）
- Git（可选但强烈建议，用来下载代码和做版本管理）
- VS Code（或你正在用的 Trae IDE）

### 2.1 如何确认安装成功（复制粘贴）

打开 PowerShell，依次运行：

```powershell
python --version
node --version
npm --version
git --version
```

你要看到类似：

- `Python 3.12.x`
- `v18.x.x`

如果提示“不是内部或外部命令”，说明没装好或没加到 PATH。

---

## 3. 你必须懂的 10 个最基础概念（小白版）

### 3.1 什么是前端/后端

- **前端**：浏览器里看到的页面（按钮、表格、弹窗）
- **后端**：处理业务逻辑的程序（保存数据、调用 AI、生成结果）

### 3.2 什么是 HTTP 请求

你点一个按钮，前端会发一个请求给后端：

- 请求方法（Method）：`GET/POST/PUT/DELETE`
- 请求地址（URL）：例如 `/api/v1/projects`
- 请求体（Body）：一般是 JSON
- 响应（Response）：后端返回 JSON

### 3.3 什么是 JSON

JSON 就是“长得像字典/对象”的文本。

例子：

```json
{"status":"ok","data":[1,2,3]}
```

### 3.4 什么是 REST API

你可以把 REST 当成一种“接口命名习惯”：

- `GET /projects`：获取项目列表
- `POST /projects`：创建一个项目
- `PUT /projects/{id}`：更新某个项目
- `DELETE /projects/{id}`：删除某个项目

### 3.5 什么是数据库

数据库就是保存数据的地方。

这项目用 **SQLite**：数据存在一个文件里（比如 `casegen.db`）。

### 3.6 什么是 ORM

ORM 就是用“类/对象”操作数据库表。

- 表 ≈ 类
- 一行数据 ≈ 类的一个实例

### 3.7 什么是异步（async/await）

异步就是：

> 遇到慢操作（网络请求、文件读写）时，不要傻等，去做别的。

在本项目里：

- 调用大模型、解析大文件、检索向量库都可能很慢
- 用 async 可以提高并发能力

### 3.8 什么是环境变量 / `.env`

环境变量就是“运行时配置”。

`.env` 文件是一个很常见的本地开发写法：

```bash
OPENAI_API_KEY=...
DEFAULT_LLM_MODEL=openai/gpt-4o
```

### 3.9 什么是依赖（requirements / npm install）

- Python 依赖：`pip install -r requirements.txt`
- 前端依赖：`npm install`

### 3.10 什么是报错栈（Traceback）

Python 报错会给你一段 Traceback：

- **最重要看最后 3 行**
- 看到 `File ... line ...` 就能定位到代码位置

---

## 4. 新手必会的排错流程（你照抄即可）

你遇到任何问题，都按这个顺序排查：

1) **我在哪个目录？**（90% 新手问题都是目录不对）

```powershell
pwd
ls
```

2) **服务有没有启动？端口是不是被占用？**

- 后端：`http://localhost:8000/health`
- 后端 Swagger：`http://localhost:8000/docs`
- 前端：`http://localhost:5173/`

3) **我有没有装依赖？**

- 后端：有没有执行 `pip install -r requirements.txt`
- 前端：有没有执行 `npm install`

4) **看日志**

- 后端启动窗口的红字
- 浏览器 F12 Console（前端错误）

5) **把错误信息复制出来**

不要只说“报错了”，要复制完整的报错文本。

---

## 5. 你如何在 IDE 里“读懂代码”（最小技能集）

你只要会 4 个操作就够：

1) 全局搜索（Ctrl+Shift+F）：找关键字
2) 跳转定义（F12 或 Ctrl+点击）：看函数/变量去哪了
3) 返回（Alt+左箭头）：回到上一个位置
4) 只看入口文件：先找 `main.py/main.ts/router`

---

## 6. 今日作业（你必须做完再进入 Day1）

1) 在 PowerShell 输出这 4 行版本号：

- `python --version`
- `node --version`
- `npm --version`
- `git --version`

2) 用浏览器打开任意一个本地服务地址（还没起服务也没关系，先认识 URL 形式）：

- `http://localhost:8000/docs`

3) 在 IDE 里用全局搜索搜索一下：

- `include_router`
- `uvicorn`
- `AiProgressModal`

你只要能做到这 3 件事，后面就不会“感觉很空”。

