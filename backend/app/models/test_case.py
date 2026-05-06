from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, generate_uuid


class TestCase(Base, TimestampMixin):
    __tablename__ = "test_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    test_point_id: Mapped[str] = mapped_column(String(36), ForeignKey("test_points.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    preconditions: Mapped[str | None] = mapped_column(Text, nullable=True)
    steps: Mapped[list] = mapped_column(JSON, nullable=False)
    priority: Mapped[str | None] = mapped_column(String(20), nullable=True)
    case_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="draft")
    generation_batch_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    project = relationship("Project", back_populates="test_cases")
    test_point = relationship("TestPoint", back_populates="test_cases")
