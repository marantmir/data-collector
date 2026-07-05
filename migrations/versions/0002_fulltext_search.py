"""add full-text search support

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-05
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("companies", sa.Column("search_vector", TSVECTOR))

    op.execute("""
        CREATE OR REPLACE FUNCTION companies_search_update() RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector('portuguese',
                COALESCE(NEW.razao_social, '') || ' ' ||
                COALESCE(NEW.nome_fantasia, '') || ' ' ||
                COALESCE(NEW.cnpj, '') || ' ' ||
                COALESCE(NEW.situacao_cadastral, '') || ' ' ||
                COALESCE(NEW.porte, '') || ' ' ||
                COALESCE(NEW.cnae_principal, '') || ' ' ||
                COALESCE(NEW.natureza_juridica, '') || ' ' ||
                COALESCE(NEW.regime_tributario, '') || ' ' ||
                COALESCE(NEW.endereco->>'cidade', '') || ' ' ||
                COALESCE(NEW.endereco->>'uf', '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER trg_companies_search
            BEFORE INSERT OR UPDATE ON companies
            FOR EACH ROW EXECUTE FUNCTION companies_search_update();
    """)

    op.create_index("idx_companies_search", "companies", ["search_vector"], postgresql_using="gin")

    op.execute("UPDATE companies SET search_vector = NULL")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_companies_search ON companies")
    op.execute("DROP FUNCTION IF EXISTS companies_search_update()")
    op.drop_index("idx_companies_search", table_name="companies")
    op.drop_column("companies", "search_vector")
