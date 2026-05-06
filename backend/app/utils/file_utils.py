import os
import aiofiles
from fastapi import UploadFile
from app.config import get_settings

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".md"}


def ensure_upload_dir(project_id: str) -> str:
    """确保项目上传目录存在"""
    project_dir = os.path.join(UPLOAD_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)
    return project_dir


def validate_file_extension(filename: str) -> str:
    """校验文件扩展名，返回文件类型"""
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"不支持的文件类型: {ext}，仅支持 PDF、DOCX、MD")
    return ext[1:]  # 去掉点号


async def save_upload_file(file: UploadFile, project_id: str) -> tuple[str, int]:
    """保存上传文件，返回 (文件路径, 文件大小)"""
    settings = get_settings()
    project_dir = ensure_upload_dir(project_id)

    # 读取文件内容
    content = await file.read()
    file_size = len(content)

    # 检查文件大小
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if file_size > max_size:
        raise ValueError(f"文件大小超过限制: {settings.MAX_UPLOAD_SIZE_MB}MB")

    file_path = os.path.join(project_dir, file.filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return file_path, file_size
