from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import FinancialResponse
from db.models.financial import FinancialStatement
from db.repository import CompanyRepository

router = APIRouter()


@router.get("/{cnpj}", response_model=list[FinancialResponse])
def get_financial_statements(
    cnpj: str,
    tipo: Optional[str] = Query(None, pattern=r"^(BALANCO|DRE|FLUXO_CAIXA)$"),
    ano_exercicio: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    repo = CompanyRepository(db)
    company = repo.get_by_cnpj(cnpj)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")

    q = db.query(FinancialStatement).filter(FinancialStatement.company_id == company.id)
    if tipo:
        q = q.filter(FinancialStatement.tipo == tipo)
    if ano_exercicio:
        q = q.filter(FinancialStatement.ano_exercicio == ano_exercicio)
    return q.all()
