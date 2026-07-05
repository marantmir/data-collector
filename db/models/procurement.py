from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import Base


class ProcurementBid(Base):
    __tablename__ = "procurement_bids"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    orgao_responsavel: Mapped[Optional[str]] = mapped_column(String(255))
    modalidade: Mapped[Optional[str]] = mapped_column(String(100))
    numero_licitacao: Mapped[Optional[str]] = mapped_column(String(100))
    objeto: Mapped[Optional[str]] = mapped_column(Text)
    valor_estimado: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    data_abertura: Mapped[Optional[str]] = mapped_column(String(10))
    data_resultado: Mapped[Optional[str]] = mapped_column(String(10))
    situacao: Mapped[Optional[str]] = mapped_column(String(50))
    vencedor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    valor_contratado: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.id")
    )

    contracts: Mapped[list[ProcurementContract]] = relationship(
        back_populates="bid", cascade="all, delete-orphan"
    )


class ProcurementContract(Base):
    __tablename__ = "procurement_contracts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bid_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("procurement_bids.id")
    )
    contractor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id")
    )
    contract_number: Mapped[Optional[str]] = mapped_column(String(100))
    object: Mapped[Optional[str]] = mapped_column(Text)
    value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2))
    start_date: Mapped[Optional[str]] = mapped_column(String(10))
    end_date: Mapped[Optional[str]] = mapped_column(String(10))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    amendments: Mapped[Optional[dict]] = mapped_column(JSONB)
    source_url: Mapped[Optional[str]] = mapped_column(Text)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("data_sources.id")
    )

    bid: Mapped[Optional[ProcurementBid]] = relationship(back_populates="contracts")
