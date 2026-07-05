from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from api.dependencies import get_db
from db.repository import CompanyRepository
from export import get_exporter

router = APIRouter()

MIME_TYPES = {
    "csv": "text/csv",
    "xml": "application/xml",
    "sped": "text/plain",
}


@router.get("/companies.{fmt}")
def export_companies(
    fmt: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=5000),
    situacao: str | None = None,
    porte: str | None = None,
    db: Session = Depends(get_db),
):
    if fmt not in MIME_TYPES:
        raise HTTPException(400, f"Formato inválido: {fmt}. Use csv, xml ou sped")

    exporter = get_exporter(fmt)
    repo = CompanyRepository(db)
    filters = {}
    if situacao:
        filters["situacao_cadastral"] = situacao
    if porte:
        filters["porte"] = porte

    companies = repo.list(skip=skip, limit=limit, **filters)
    content = exporter.export_companies(companies)

    return Response(
        content=content,
        media_type=MIME_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="empresas.{fmt}"'},
    )


@router.get("/companies/{cnpj}.{fmt}")
def export_company(
    cnpj: str,
    fmt: str,
    db: Session = Depends(get_db),
):
    if fmt not in MIME_TYPES:
        raise HTTPException(400, f"Formato inválido: {fmt}")

    repo = CompanyRepository(db)
    company = repo.get_by_cnpj(cnpj)
    if not company:
        raise HTTPException(404, "Empresa não encontrada")

    exporter = get_exporter(fmt)
    content = exporter.export_company(company)

    return Response(
        content=content,
        media_type=MIME_TYPES[fmt],
        headers={"Content-Disposition": f'attachment; filename="{cnpj}.{fmt}"'},
    )
