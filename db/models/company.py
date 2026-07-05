from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base, TimestampMixin


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cnpj: Mapped[str] = mapped_column(String(14), unique=True, nullable=False, index=True)
    razao_social: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_fantasia: Mapped[Optional[str]] = mapped_column(String(255))
    cnae_principal: Mapped[Optional[str]] = mapped_column(String(7))
    cnae_secundarias: Mapped[Optional[dict]] = mapped_column(JSONB)
    natureza_juridica: Mapped[Optional[str]] = mapped_column(String(100))
    porte: Mapped[Optional[str]] = mapped_column(String(20))
    situacao_cadastral: Mapped[Optional[str]] = mapped_column(String(50))
    data_situacao: Mapped[Optional[str]] = mapped_column(String(10))
    regime_tributario: Mapped[Optional[str]] = mapped_column(String(50))
    capital_social: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    endereco: Mapped[Optional[dict]] = mapped_column(JSONB)
    contato: Mapped[Optional[dict]] = mapped_column(JSONB)
    search_vector: Mapped[Optional[str]] = mapped_column(TSVECTOR, index=True)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.id")
    )

    partners: Mapped[list[Partner]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
    financial_statements: Mapped[list[FinancialStatement]] = relationship(
        back_populates="company", cascade="all, delete-orphan"
    )
