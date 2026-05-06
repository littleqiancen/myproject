import asyncio
import logging
from app.config import get_settings

logger = logging.getLogger(__name__)

_local_model = None  # lazy singleton


def _get_local_model():
    global _local_model
    if _local_model is None:
        from sentence_transformers import SentenceTransformer
        settings = get_settings()
        _local_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"已加载本地 Embedding 模型: {settings.EMBEDDING_MODEL}")
    return _local_model


async def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of texts."""
    settings = get_settings()
    if settings.EMBEDDING_PROVIDER == "openai":
        return await _embed_via_litellm(texts)
    else:
        return await _embed_local(texts)


async def _embed_local(texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_event_loop()
    model = _get_local_model()
    embeddings = await loop.run_in_executor(
        None, lambda: model.encode(texts).tolist()
    )
    return embeddings


async def _embed_via_litellm(texts: list[str]) -> list[list[float]]:
    import litellm
    settings = get_settings()
    response = await litellm.aembedding(
        model=settings.EMBEDDING_MODEL,
        input=texts,
        api_key=settings.OPENAI_API_KEY,
    )
    return [item["embedding"] for item in response.data]
