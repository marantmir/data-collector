from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class FinancialStatement(Base):
    __tablename__ = "financial_statements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    ano_exercicio: Mapped[int] = mapped_column(Integer, nullable=False)
    trimestre: Mapped[Optional[int]] = mapped_column(Integer)
    data_referencia: Mapped[str] = mapped_column(String(10), nullable=False)
    valores: Mapped[dict] = mapped_column(JSONB, nullable=False)
    moeda: Mapped[str] = mapped_column(String(3), default="BRL")
    audited: Mapped[bool] = mapped_column(Boolean, default=False)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.id")
    )

    company: Mapped[Company] = relationship(back_populates="financial_statements")
