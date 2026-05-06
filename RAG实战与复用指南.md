# RAG (检索增强生成) 实战与复用指南

这份教程结合了当前项目中的实际代码，带你从0到1理解并掌握 RAG（Retrieval-Augmented Generation）的编写方式，帮助你在以后的任何新项目中都能快速复用这套代码架构。

---

## 1. 什么是 RAG？(大白话解释)

大语言模型（LLM）像一个博学的大学生，但他没有看过你们公司的内部机密文件（比如接口文档、内部规范）。如果你直接问他“怎么测试我们的登录接口？”，他要么说不知道，要么“幻觉”胡编乱造。

**RAG 的核心思想就是“开卷考试”**：
1. **建库（Indexing）**：把你们公司的私有文档切成一页一页的小抄，存到一个特殊的图书馆里（向量数据库）。
2. **检索（Retrieval）**：当用户提问时，先去图书馆里把和问题最相关的几页小抄找出来。
3. **生成（Generation）**：把问题和找出来的小抄一起打包，丢给大模型说：“**根据这几页参考资料**，回答用户的问题。”

在代码层面，RAG 永远由三个核心模块组成：**文档解析 → 向量化入库 → 检索拼接 Prompt**。

---

## 2. 核心代码位置清单

在这个项目中，RAG 相关的代码非常内聚，主要分布在 `backend/app/services` 目录下的这几个文件里：

1. **`ai/document_parser.py`**：负责“拆书”，把 PDF/Word 转成纯文本 Markdown。
2. **`rag_service.py`**：核心枢纽。负责“文本切片 (Chunking)”、“连接向量库 (ChromaDB)”、“存数据”和“查数据”。
3. **`ai/embedding_service.py`**：负责“向量化 (Embedding)”，把文字变成一串多维数字（比如 [0.12, -0.45...]）。

---

## 3. RAG 核心三步曲 (结合代码讲解)

### 第一步：文档解析与切片 (Data Parsing & Chunking)

大模型处理不了花里胡哨的 PDF 排版，而且如果文件有几百页，一次性塞给大模型会撑爆它的上下文（Context Window）。所以必须提取纯文本，并切成“块（Chunk）”。

**1. 提取纯文本：**
在 `document_parser.py` 中，我们用 `pymupdf4llm` 解析 PDF，用 `python-docx` 解析 Word，统一转成带层级的 Markdown 文本。
> **避坑点**：PDF 里的表格很难解析，`pymupdf4llm` 相比普通的 PyPDF2 能更好地保留表格 Markdown 格式，这是 RAG 质量的保证。

**2. 文本切片 (Chunking)：**
看 `rag_service.py` 里的 `chunk_text` 方法：
```python
def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 64) -> list[str]:
    # 把长文本切成 512 字符一块，但每两块之间必须有 64 个字符的“重叠”
    ...
```
> **为什么要重叠（Overlap）？**
> 假设一句话是“服务器的密码是123456”。如果刚好切在“密码是”和“123456”中间，这句话就废了。留 64 个字符的重叠，就像盖瓦片一样，保证上下文不会被一刀切断。

### 第二步：向量化与存入数据库 (Embedding & Indexing)

切好片之后，要把文字转成“向量”，存到向量数据库 ChromaDB 里。

**1. 生成词向量 (Embedding)：**
在 `embedding_service.py` 里，你可以看到：
```python
# 本地模型方案（免费，不用调 API）
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(texts).tolist()
```
> **Embedding 的原理**：它是把一段文字映射到多维空间里的一个点。意思越相近的两段话，它们在空间里的距离就越近。

**2. 存入 ChromaDB：**
在 `rag_service.py` 里的 `index_document` 方法：
```python
    client = chromadb.PersistentClient(path=persist_dir)
    # 为当前知识库建立一个独立的集合（Collection），物理隔离防串味
    collection = client.get_or_create_collection(name=f"kb_{kb_id}")
    
    collection.add(
        ids=[f"chunk_{i}"],          # 唯一主键
        embeddings=embeddings,       # 刚生成的向量矩阵
        documents=chunks,            # 原始文本片段
        metadatas=[{"source": filename}] # 元数据（比如它来自哪个文件，用于后期溯源）
    )
```

### 第三步：检索与拼接 Prompt (Retrieval & Generation)

当你要生成测试用例时，就要去库里捞数据了。

**1. 检索相似度最高的小抄 (Top-K)：**
看 `rag_service.py` 里的 `retrieve` 方法：
```python
async def retrieve(knowledge_base_ids: list[str], query: str, top_k: int = 5) -> list[dict]:
    # 1. 把用户的提问（Query）也转成向量
    query_embedding = generate_embeddings([query])[0]
    
    # 2. 去 ChromaDB 里搜索距离这个 Query 向量最近的 5 个点
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k, # 取 Top-5
    )
    # 返回搜到的文本和它的来源文件名
    ...
```

**2. 拼接 Prompt 丢给大模型：**
这是最关键的“开卷考试”环节。看业务代码 `test_case_generator.py` 里是怎么组装 Prompt 的：
```python
    # 1. 把检索出来的 5 段话，用字符串拼接起来
    rag_chunks = "\n\n".join(f"[来源: {c['source_filename']}]\n{c['text']}" for c in chunks)
    
    # 2. 塞进定义好的 Prompt 模板里
    rag_context = f"""
    ---
    以下是从知识库中检索到的相关参考资料，请结合这些信息生成用例：
    {rag_chunks}
    ---
    """
    
    # 3. 加上用户原始的提问，一起丢给大模型
    user_prompt = f"测试点：{title} \n {rag_context} \n 请生成用例。"
```

---

## 4. 下次写新项目，如何快速复用这套 RAG？

不管你下一个项目是做“智能客服”、“企业知识库问答”还是“代码审查助手”，RAG 的代码都可以直接从这个项目里“Ctrl+C / Ctrl+V”。

**复用清单与步骤：**

1. **抄走 `rag_service.py` 和 `embedding_service.py`**。
   - 这两个文件是完全解耦的，基本不依赖业务表结构。
   - 你只需要在你的新项目里安装依赖：`pip install chromadb sentence-transformers`。
   
2. **抄走 `document_parser.py`**。
   - 这是一套久经考验的文件解析器。新项目里安装 `pymupdf4llm` 和 `python-docx` 就能直接复用。

3. **在新项目中定义“两套接口”**：
   - **建库接口**：照抄 `upload_kb_documents`。接收用户文件 -> 调 parser 解析 -> 调 `rag_service.index_document` 存进去。
   - **查询接口**：接收用户提问 -> 调 `rag_service.retrieve` 查出资料 -> 拼接到你的 Prompt 模板里 -> 调 OpenAI/DeepSeek 接口返回回答。

**高级架构建议（新项目避坑）：**
- **不要阻塞主线程**：不管是解析 PDF、本地生成 Embedding 还是写 ChromaDB，都是 CPU 密集型操作。在 FastAPI 里，必须像本项目一样使用 `asyncio.get_event_loop().run_in_executor` 放进线程池里跑，否则你的整个 Web 服务会卡死。
- **物理隔离**：一定要保留本项目里 `_get_collection_name(kb_id)` 这个设计。很多新手把所有用户的文档全 `add()` 到同一个 Collection 里，结果 A 公司的客服搜出了 B 公司的机密文档。一人/一项目一个 Collection 是最安全的做法。