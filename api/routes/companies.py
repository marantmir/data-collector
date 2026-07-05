from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import CompanyListResponse, CompanyResponse
from db.models.company import Company
from db.repository import CompanyRepository

router = APIRouter()


@router.get("/search", response_model=CompanyListResponse)
def search_companies(
    q: str = Query(..., min_length=1, max_length=200),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query_ts = func.plainto_tsquery("portuguese", q)
    rank = func.ts_rank(Company.search_vector, query_ts)

    total = (
        db.query(func.count(Company.id))
        .filter(Company.search_vector.op("@@")(query_ts))
        .scalar()
        or 0
    )

    items = (
        db.query(Company)
        .filter(Company.search_vector.op("@@")(query_ts))
        .order_by(rank.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    return CompanyListResponse(
        items=[CompanyResponse.model_validate(c) for c in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("", response_model=CompanyListResponse)
def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    situacao: Optional[str] = None,
    porte: Optional[str] = None,
    cnae: Optional[str] = None,
    cidade: Optional[str] = None,
    uf: Optional[str] = None,
    db: Session = Depends(get_db),
):
    repo = CompanyRepository(db)
    filters = {}
    if situacao:
        filters["situacao_cadastral"] = situacao
    if porte:
        filters["porte"] = porte
    if cnae:
        filters["cnae_principal"] = cnae
    items = repo.list(skip=skip, limit=limit, **filters)
    total = repo.count(**filters)

    if cidade:
        items = [c for c in items if c.endereco and c.endereco.get("cidade", "").lower() == cidade.lower()]
        total = len(items)

    return CompanyListResponse(
        items=[CompanyResponse.model_validate(c) for c in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{cnpj}", response_model=CompanyResponse)
def get_company(cnpj: str, db: Session = Depends(get_db)):
    repo = CompanyRepository(db)
    company = repo.get_by_cnpj(cnpj)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return company


@router.get("/{cnpj}/partners", response_model=list[dict])
def get_company_partners(cnpj: str, db: Session = Depends(get_db)):
    repo = CompanyRepository(db)
    company = repo.get_by_cnpj(cnpj)
    if not company:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return [
        {
            "nome": p.nome,
            "cpf_cnpj": p.cpf_cnpj,
            "qualificacao": p.qualificacao,
            "percentual": str(p.percentual) if p.percentual else None,
        }
        for p in company.partners
    ]
