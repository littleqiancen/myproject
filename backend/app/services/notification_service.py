from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse
from app.integrations.feishu import send_feishu_message
from app.config import get_settings


async def get_notifications(
    db: AsyncSession, project_id: str
) -> tuple[list[NotificationResponse], int]:
    count_result = await db.execute(
        select(func.count(Notification.id)).where(Notification.project_id == project_id)
    )
    total = count_result.scalar()

    result = await db.execute(
        select(Notification)
        .where(Notification.project_id == project_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    notifications = result.scalars().all()
    return [NotificationResponse.model_validate(n) for n in notifications], total


async def send_notification(
    db: AsyncSession,
    project_id: str,
    event_type: str,
    content: dict,
    webhook_url: str | None = None,
    webhook_secret: str | None = None,
) -> None:
    settings = get_settings()
    url = webhook_url or settings.FEISHU_WEBHOOK_URL
    secret = webhook_secret or settings.FEISHU_WEBHOOK_SECRET

    if not url:
        return  # 未配置飞书webhook，跳过通知

    notification = Notification(
        project_id=project_id,
        event_type=event_type,
        payload=content,
        status="pending",
    )
    db.add(notification)
    await db.commit()

    try:
        await send_feishu_message(url, content, secret)
        notification.status = "sent"
        from datetime import datetime
        notification.sent_at = datetime.now()
    except Exception as e:
        notification.status = "failed"
        notification.error_message = str(e)

    await db.commit()
