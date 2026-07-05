import logging
from typing import Optional

from sqlalchemy.orm import Session

from db.models.company import Company
from enrichment.scorer import ReliabilityScorer
from sources import get_connector

logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    def __init__(self, db: Session):
        self.db = db
        self.scorer = ReliabilityScorer()

    def enrich(self, cnpj: str) -> Optional[Company]:
        company = self.db.query(Company).filter(Company.cnpj == cnpj).first()
        if not company:
            logger.warning(f"CNPJ {cnpj} não encontrado no banco")
            return None

        sources_data = {}

        for source_name in ["brasilapi", "cnpja"]:
            try:
                connector = get_connector(source_name)
                data = connector.fetch_company(cnpj)
                sources_data[source_name] = {
                    "data": data,
                    "score": self.scorer.score_source(source_name, data),
                }
                logger.info(f"  {source_name}: score {sources_data[source_name]['score']}")
            except Exception as e:
                logger.warning(f"  {source_name}: falhou - {e}")

        if sources_data:
            best = max(sources_data.values(), key=lambda x: x["score"])
            self._apply_enrichment(company, best["data"], best["score"])
            self.db.commit()
            logger.info(f"Enriquecido {cnpj} com score {best['score']}")

        return company

    def enrich_batch(self, cnpjs: list[str], max_workers: int = 5) -> dict:
        results = {"success": 0, "failed": 0, "skipped": 0}
        for cnpj in cnpjs:
            try:
                result = self.enrich(cnpj)
                if result:
                    results["success"] += 1
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Erro ao enriquecer {cnpj}: {e}")
                results["failed"] += 1
        return results

    def _apply_enrichment(self, company: Company, data, score: float) -> None:
        if not company.nome_fantasia and data.nome_fantasia:
            company.nome_fantasia = data.nome_fantasia
        if not company.cnae_principal and data.cnae_principal:
            company.cnae_principal = data.cnae_principal
        if not company.porte and data.porte:
            company.porte = data.porte
        if not company.situacao_cadastral and data.situacao_cadastral:
            company.situacao_cadastral = data.situacao_cadastral
        if not company.natureza_juridica and data.natureza_juridica:
            company.natureza_juridica = data.natureza_juridica
        if not company.regime_tributario and data.regime_tributario:
            company.regime_tributario = data.regime_tributario
