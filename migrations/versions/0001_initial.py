"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-05
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "data_sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("type", sa.String(50)),
        sa.Column("base_url", sa.Text),
        sa.Column("description", sa.Text),
        sa.Column("reliability_score", sa.Numeric(3, 2)),
        sa.Column("active", sa.Boolean(), default=True),
        sa.Column("config", JSONB),
    )

    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("cnpj", sa.String(14), unique=True, nullable=False, index=True),
        sa.Column("razao_social", sa.String(255), nullable=False),
        sa.Column("nome_fantasia", sa.String(255)),
        sa.Column("cnae_principal", sa.String(7)),
        sa.Column("cnae_secundarias", JSONB),
        sa.Column("natureza_juridica", sa.String(10)),
        sa.Column("porte", sa.String(20)),
        sa.Column("situacao_cadastral", sa.String(50)),
        sa.Column("data_situacao", sa.String(10)),
        sa.Column("regime_tributario", sa.String(50)),
        sa.Column("capital_social", sa.Numeric(18, 2)),
        sa.Column("endereco", JSONB),
        sa.Column("contato", JSONB),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_table(
        "partners",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("cpf_cnpj", sa.String(14)),
        sa.Column("nome", sa.String(255), nullable=False),
        sa.Column("qualificacao", sa.String(100)),
        sa.Column("percentual", sa.Numeric(5, 2)),
        sa.Column("data_entrada", sa.String(10)),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id")),
    )

    op.create_table(
        "financial_statements",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "company_id",
            UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("ano_exercicio", sa.Integer(), nullable=False),
        sa.Column("trimestre", sa.Integer()),
        sa.Column("data_referencia", sa.String(10), nullable=False),
        sa.Column("valores", JSONB, nullable=False),
        sa.Column("moeda", sa.String(3), default="BRL"),
        sa.Column("audited", sa.Boolean(), default=False),
        sa.Column("source_url", sa.Text),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id")),
    )

    op.create_table(
        "procurement_bids",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("company_id", UUID(as_uuid=True), sa.ForeignKey("companies.id")),
        sa.Column("orgao_responsavel", sa.String(255)),
        sa.Column("modalidade", sa.String(100)),
        sa.Column("numero_licitacao", sa.String(100)),
        sa.Column("objeto", sa.Text),
        sa.Column("valor_estimado", sa.Numeric(18, 2)),
        sa.Column("data_abertura", sa.String(10)),
        sa.Column("data_resultado", sa.String(10)),
        sa.Column("situacao", sa.String(50)),
        sa.Column("vencedor_id", UUID(as_uuid=True), sa.ForeignKey("companies.id")),
        sa.Column("valor_contratado", sa.Numeric(18, 2)),
        sa.Column("source_url", sa.Text),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id")),
    )

    op.create_table(
        "procurement_contracts",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("bid_id", UUID(as_uuid=True), sa.ForeignKey("procurement_bids.id")),
        sa.Column("contractor_id", UUID(as_uuid=True), sa.ForeignKey("companies.id")),
        sa.Column("contract_number", sa.String(100)),
        sa.Column("object", sa.Text),
        sa.Column("value", sa.Numeric(18, 2)),
        sa.Column("start_date", sa.String(10)),
        sa.Column("end_date", sa.String(10)),
        sa.Column("status", sa.String(50)),
        sa.Column("amendments", JSONB),
        sa.Column("source_url", sa.Text),
        sa.Column("source_id", UUID(as_uuid=True), sa.ForeignKey("data_sources.id")),
    )

    op.create_table(
        "collection_jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("source_id", UUID(as_uuid=True)),
        sa.Column("spider_name", sa.String(100)),
        sa.Column("status", sa.String(20)),
        sa.Column("items_collected", sa.Integer(), default=0),
        sa.Column("items_failed", sa.Integer(), default=0),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("error_log", sa.Text),
        sa.Column("meta", JSONB),
    )

    op.create_table(
        "audit_log",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("table_name", sa.String(50), nullable=False),
        sa.Column("record_id", UUID(as_uuid=True), nullable=False),
        sa.Column("operation", sa.String(10), nullable=False),
        sa.Column("old_values", JSONB),
        sa.Column("new_values", JSONB),
        sa.Column("changed_by", sa.String(100)),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )

    op.create_index(
        "idx_financial_company", "financial_statements", ["company_id", "tipo", "ano_exercicio"]
    )
    op.create_index(
        "idx_bids_orgao", "procurement_bids", ["orgao_responsavel", "numero_licitacao"], unique=True
    )


def downgrade() -> None:
    op.drop_table("audit_log")
    op.drop_table("collection_jobs")
    op.drop_table("procurement_contracts")
    op.drop_table("procurement_bids")
    op.drop_table("financial_statements")
    op.drop_table("partners")
    op.drop_table("companies")
    op.drop_table("data_sources")
