from config import settings

BOT_NAME = "data_collector"
SPIDER_MODULES = ["crawlers.spiders"]
NEWSPIDER_MODULE = "crawlers.spiders"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

CONCURRENT_REQUESTS = settings.crawler_concurrent_requests
DOWNLOAD_DELAY = settings.crawler_download_delay

COOKIES_ENABLED = False
TELNETCONSOLE_ENABLED = False

DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

SPIDER_MIDDLEWARES = {}

DOWNLOADER_MIDDLEWARES = {
    "crawlers.middlewares.RandomUserAgentMiddleware": 400,
    "crawlers.middlewares.SmartRetryMiddleware": 500,
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
}

ITEM_PIPELINES = {
    "crawlers.pipelines.DatabasePipeline": 300,
}

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 30.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0

EXTENSIONS = {
    "scrapy.extensions.telnet.TelnetConsole": None,
}

LOG_LEVEL = settings.log_level
