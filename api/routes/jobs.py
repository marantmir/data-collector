from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies import get_db
from db.models.audit import CollectionJob

router = APIRouter()


class JobResponse(BaseModel):
    id: str
    source_id: str | None = None
    spider_name: str | None = None
    status: str | None = None
    items_collected: int = 0
    items_failed: int = 0
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_log: str | None = None
    meta: dict | None = None
    duration_seconds: float | None = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    running: int
    completed: int
    failed: int


class JobCreate(BaseModel):
    spider_name: str = "cadastral"
    cnpjs: list[str] | None = None
    source_id: str | None = None


def _format_job(job: CollectionJob) -> JobResponse:
    duration = None
    if job.started_at and job.finished_at:
        duration = (job.finished_at - job.started_at).total_seconds()
    return JobResponse(
        id=str(job.id),
        source_id=str(job.source_id) if job.source_id else None,
        spider_name=job.spider_name,
        status=job.status,
        items_collected=job.items_collected or 0,
        items_failed=job.items_failed or 0,
        started_at=job.started_at,
        finished_at=job.finished_at,
        error_log=job.error_log,
        meta=job.meta,
        duration_seconds=round(duration, 2) if duration is not None else None,
    )


@router.get("", response_model=JobListResponse)
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    spider: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(CollectionJob)
    if status:
        q = q.filter(CollectionJob.status == status)
    if spider:
        q = q.filter(CollectionJob.spider_name == spider)

    total = q.count()
    running = db.query(CollectionJob).filter(CollectionJob.status == "running").count()
    completed = db.query(CollectionJob).filter(CollectionJob.status == "completed").count()
    failed = db.query(CollectionJob).filter(CollectionJob.status == "failed").count()

    items = q.order_by(CollectionJob.started_at.desc().nullslast()).offset(skip).limit(limit).all()

    return JobListResponse(
        items=[_format_job(j) for j in items],
        total=total,
        running=running,
        completed=completed,
        failed=failed,
    )


@router.get("/spiders", response_model=list[dict])
def list_spiders():
    return [
        {"name": "cadastral", "label": "Dados Cadastrais", "description": "Coleta dados cadastrais de empresas via BrasilAPI/CNPJa"},
        {"name": "financial", "label": "Demonstrações Financeiras", "description": "Coleta demonstrações financeiras (DRE, balanço)"},
        {"name": "procurement", "label": "Licitações e Contratos", "description": "Coleta dados de licitações e contratos públicos"},
    ]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "ID inválido")
    job = db.query(CollectionJob).filter(CollectionJob.id == uid).first()
    if not job:
        raise HTTPException(404, "Job não encontrado")
    return _format_job(job)


@router.post("", response_model=JobResponse, status_code=201)
def create_job(data: JobCreate, db: Session = Depends(get_db)):
    job = CollectionJob(
        source_id=uuid.UUID(data.source_id) if data.source_id else None,
        spider_name=data.spider_name,
        status="pending",
        started_at=datetime.now(timezone.utc),
        meta={"cnpjs": data.cnpjs} if data.cnpjs else None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return _format_job(job)


@router.post("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(job_id: str, db: Session = Depends(get_db)):
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "ID inválido")
    job = db.query(CollectionJob).filter(CollectionJob.id == uid).first()
    if not job:
        raise HTTPException(404, "Job não encontrado")
    if job.status not in ("pending", "running"):
        raise HTTPException(400, f"Job {job.status} não pode ser cancelado")
    job.status = "cancelled"
    job.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)
    return _format_job(job)


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    try:
        uid = uuid.UUID(job_id)
    except ValueError:
        raise HTTPException(400, "ID inválido")
    job = db.query(CollectionJob).filter(CollectionJob.id == uid).first()
    if not job:
        raise HTTPException(404, "Job não encontrado")
    db.delete(job)
    db.commit()
