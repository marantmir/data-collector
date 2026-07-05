from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class Partner(Base):
    __tablename__ = "partners"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    cpf_cnpj: Mapped[Optional[str]] = mapped_column(String(14))
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    qualificacao: Mapped[Optional[str]] = mapped_column(String(100))
    percentual: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2))
    data_entrada: Mapped[Optional[str]] = mapped_column(String(10))
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.id")
    )

    company: Mapped[Company] = relationship(back_populates="partners")
