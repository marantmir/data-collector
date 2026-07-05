from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.schemas import BidResponse
from db.models.procurement import ProcurementBid

router = APIRouter()


@router.get("/bids", response_model=list[BidResponse])
def list_bids(
    orgao: Optional[str] = None,
    modalidade: Optional[str] = None,
    situacao: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    q = db.query(ProcurementBid)
    if orgao:
        q = q.filter(ProcurementBid.orgao_responsavel.ilike(f"%{orgao}%"))
    if modalidade:
        q = q.filter(ProcurementBid.modalidade == modalidade)
    if situacao:
        q = q.filter(ProcurementBid.situacao == situacao)
    return q.offset(skip).limit(limit).all()
