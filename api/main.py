from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from api.routes.companies import router as companies_router
from api.routes.enrichment import router as enrichment_router
from api.routes.export import router as export_router
from api.routes.financial import router as financial_router
from api.routes.jobs import router as jobs_router
from api.routes.procurement import router as procurement_router
from webhooks.router import router as webhooks_router

app = FastAPI(
    title="Data Collector API",
    description="API de consulta de dados empresariais coletados da web",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


app.include_router(companies_router, prefix="/api/v1/companies", tags=["Companies"])
app.include_router(enrichment_router, prefix="/api/v1", tags=["Enrichment"])
app.include_router(export_router, prefix="/api/v1/export", tags=["Export"])
app.include_router(financial_router, prefix="/api/v1/financial", tags=["Financial"])
app.include_router(jobs_router, prefix="/api/v1/jobs", tags=["Jobs"])
app.include_router(procurement_router, prefix="/api/v1/procurement", tags=["Procurement"])
app.include_router(webhooks_router, prefix="/api/v1", tags=["Webhooks"])
app.mount("/", StaticFiles(directory="static", html=True), name="static")
