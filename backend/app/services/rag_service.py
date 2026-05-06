import asyncio
import logging
import os
from typing import Optional
import chromadb
from app.config import get_settings
from app.services.ai.embedding_service import generate_embeddings

logger = logging.getLogger(__name__)

_chroma_client: Optional[chromadb.ClientAPI] = None


def get_chroma_client() -> chromadb.ClientAPI:
    global _chroma_client
    if _chroma_client is None:
        settings = get_settings()
        persist_dir = os.path.abspath(settings.CHROMADB_PATH)
        os.makedirs(persist_dir, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
        logger.info(f"ChromaDB 初始化完成: {persist_dir}")
    return _chroma_client


def _get_collection_name(knowledge_base_id: str) -> str:
    return f"kb_{knowledge_base_id.replace('-', '_')}"


def chunk_text(text: str, chunk_size: int = 512, chunk_overlap: int = 64) -> list[str]:
    """将文本按字符分块，chunk_size/chunk_overlap 以 token 为单位（近似 4 字符/token）"""
    if not text:
        return []

    chars_chunk = chunk_size * 4
    chars_overlap = chunk_overlap * 4

    chunks = []
    start = 0
    while start < len(text):
        end = start + chars_chunk
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk.strip())
        start = end - chars_overlap
        if start >= len(text):
            break

    return chunks


async def index_document(
    knowledge_base_id: str,
    kb_document_id: str,
    filename: str,
    text: str,
) -> int:
    """分块、embedding 并存入 ChromaDB。返回 chunk 数量。"""
    settings = get_settings()
    chunks = chunk_text(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)

    if not chunks:
        return 0

    embeddings = await generate_embeddings(chunks)

    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=_get_collection_name(knowledge_base_id),
        metadata={"hnsw:space": "cosine"},
    )

    ids = [f"{kb_document_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {"source_filename": filename, "kb_document_id": kb_document_id, "chunk_index": i}
        for i in range(len(chunks))
    ]

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        ),
    )

    return len(chunks)


async def delete_document_chunks(knowledge_base_id: str, kb_document_id: str) -> None:
    """删除 ChromaDB 中某文档的所有分块"""
    client = get_chroma_client()
    col_name = _get_collection_name(knowledge_base_id)
    try:
        collection = client.get_collection(col_name)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: collection.delete(where={"kb_document_id": kb_document_id}),
        )
    except Exception:
        pass


async def delete_collection(knowledge_base_id: str) -> None:
    """删除整个知识库的 ChromaDB collection"""
    client = get_chroma_client()
    col_name = _get_collection_name(knowledge_base_id)
    try:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: client.delete_collection(col_name))
    except Exception:
        pass


async def retrieve(
    knowledge_base_ids: list[str],
    query: str,
    top_k: int | None = None,
) -> list[dict]:
    """从多个知识库中检索最相关的 top_k 个分块。

    返回 [{"text": str, "source_filename": str, "score": float}]
    """
    settings = get_settings()
    if top_k is None:
        top_k = settings.RAG_TOP_K

    query_embedding = (await generate_embeddings([query]))[0]

    all_results = []
    client = get_chroma_client()

    for kb_id in knowledge_base_ids:
        col_name = _get_collection_name(kb_id)
        try:
            collection = client.get_collection(col_name)
        except Exception:
            continue

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda col=collection: col.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=["documents", "metadatas", "distances"],
            ),
        )

        if results and results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                all_results.append({
                    "text": doc,
                    "source_filename": meta.get("source_filename", "unknown"),
                    "score": 1 - dist,  # cosine distance → similarity
                })

    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[:top_k]
