from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies import get_db
from db.repository import CompanyRepository
from enrichment.pipeline import EnrichmentPipeline

router = APIRouter()


class EnrichResponse(BaseModel):
    cnpj: str
    status: str
    score: float | None = None
    message: str | None = None


@router.post("/enrich/{cnpj}", response_model=EnrichResponse)
def enrich_company(cnpj: str, db: Session = Depends(get_db)):
    repo = CompanyRepository(db)
    company = repo.get_by_cnpj(cnpj)
    if not company:
        raise HTTPException(404, "Empresa não encontrada no banco")

    pipeline = EnrichmentPipeline(db)
    result = pipeline.enrich(cnpj)

    if result:
        return EnrichResponse(cnpj=cnpj, status="enriched", score=0.9, message="Dados enriquecidos com sucesso")
    return EnrichResponse(cnpj=cnpj, status="failed", message="Falha no enriquecimento")


@router.post("/enrich/batch", response_model=dict)
def enrich_batch(cnpjs: list[str], db: Session = Depends(get_db)):
    pipeline = EnrichmentPipeline(db)
    return pipeline.enrich_batch(cnpjs)
