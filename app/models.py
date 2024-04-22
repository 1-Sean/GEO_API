from typing import Optional
from geoalchemy2 import Geometry
from sqlalchemy import String, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

# from app.database import Base
import uuid


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"schema": "project_data"}

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    start_date: Mapped[Date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Date] = mapped_column(Date, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[DateTime]] = mapped_column(
        DateTime, onupdate=func.now(), nullable=True
    )
    aoi: Mapped[Geometry] = mapped_column(
        Geometry("MULTIPOLYGON", srid=4326), nullable=False
    )
