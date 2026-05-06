from pydantic import BaseModel
from datetime import datetime


class NotificationResponse(BaseModel):
    id: str
    project_id: str
    event_type: str
    channel: str
    payload: dict | None = None
    status: str
    error_message: str | None = None
    sent_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int


class TestNotificationRequest(BaseModel):
    webhook_url: str
    webhook_secret: str | None = None
