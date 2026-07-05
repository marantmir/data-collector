#!/usr/bin/env python3
"""
Script para popular o banco com dados reais de empresas via BrasilAPI.

Uso:
    python scripts/seed_from_api.py 00000000000191 11222333000181
"""
import argparse
import logging

from db.models.company import Company
from db.models.partner import Partner
from db.models.source import DataSource
from db.session import SessionLocal
from etl.validators import sanitize_cnpj, validate_cnpj
from sources import get_connector

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def seed(cnpjs: list[str], source_name: str = "brasilapi") -> None:
    connector = get_connector(source_name)
    db = SessionLocal()

    source = db.query(DataSource).filter(DataSource.name == source_name).first()
    if not source:
        source = DataSource(
            name=source_name,
            type="API",
            base_url=getattr(connector, "base_url", ""),
            description=f"Dados via {source_name}",
            active=True,
        )
        db.add(source)
        db.flush()

    for cnpj in cnpjs:
        cnpj_clean = sanitize_cnpj(cnpj)
        if not validate_cnpj(cnpj_clean):
            logger.warning(f"CNPJ inválido: {cnpj}")
            continue

        existing = db.query(Company).filter(Company.cnpj == cnpj_clean).first()
        if existing:
            logger.info(f"CNPJ {cnpj_clean} já existe, pulando...")
            continue

        try:
            company_data = connector.fetch_company(cnpj_clean)
        except Exception as e:
            logger.error(f"Erro ao buscar CNPJ {cnpj_clean}: {e}")
            continue

        company = Company(
            cnpj=company_data.cnpj,
            razao_social=company_data.razao_social,
            nome_fantasia=company_data.nome_fantasia,
            cnae_principal=company_data.cnae_principal,
            cnae_secundarias=company_data.cnae_secundarias,
            natureza_juridica=company_data.natureza_juridica,
            porte=company_data.porte,
            situacao_cadastral=company_data.situacao_cadastral,
            data_situacao=company_data.data_situacao,
            regime_tributario=company_data.regime_tributario,
            capital_social=company_data.capital_social,
            endereco=company_data.endereco,
            contato=company_data.contato,
            source_id=source.id,
        )
        db.add(company)
        db.flush()
        logger.info(f"Empresa salva: {company_data.razao_social} ({company_data.cnpj})")

        for socio in company_data.socios:
            partner = Partner(
                company_id=company.id,
                cpf_cnpj=socio.cpf_cnpj,
                nome=socio.nome,
                qualificacao=socio.qualificacao,
                percentual=socio.percentual,
                data_entrada=socio.data_entrada,
                source_id=source.id,
            )
            db.add(partner)

        db.commit()
        logger.info(f"  + {len(company_data.socios)} sócio(s) salvos")

    db.close()


def main():
    parser = argparse.ArgumentParser(description="Popula banco com dados reais de CNPJs")
    parser.add_argument("cnpjs", nargs="+", help="CNPJs para buscar (com ou sem formatação)")
    parser.add_argument("--source", default="brasilapi", choices=["brasilapi", "cnpja"], help="Fonte de dados")
    args = parser.parse_args()
    seed(args.cnpjs, args.source)


if __name__ == "__main__":
    main()
