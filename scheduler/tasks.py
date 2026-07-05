import uuid

from celery import Celery
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from config import settings

app = Celery("data_collector", broker=settings.redis_url, backend=settings.redis_url)

app.conf.beat_schedule = {
    "collect-cadastral-daily": {
        "task": "scheduler.tasks.run_cadastral_spider",
        "schedule": 86400.0,
    },
    "collect-procurement-hourly": {
        "task": "scheduler.tasks.run_procurement_spider",
        "schedule": 3600.0,
    },
}


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def run_cadastral_spider(self, cnpjs: str | None = None) -> dict:
    source_id = uuid.uuid4()
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl("cadastral", cnpjs=cnpjs, source_id=str(source_id))
    process.start()
    return {"status": "completed", "spider": "cadastral", "source_id": str(source_id)}


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def run_financial_spider(self, cnpjs: str) -> dict:
    source_id = uuid.uuid4()
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl("financial", cnpjs=cnpjs, source_id=str(source_id))
    process.start()
    return {"status": "completed", "spider": "financial", "source_id": str(source_id)}


@app.task(bind=True, max_retries=3, default_retry_delay=300)
def run_procurement_spider(self) -> dict:
    source_id = uuid.uuid4()
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl("procurement", source_id=str(source_id))
    process.start()
    return {"status": "completed", "spider": "procurement", "source_id": str(source_id)}
