from prometheus_client import Counter, Gauge, Histogram

COMPANIES_COLLECTED = Counter(
    "companies_collected_total",
    "Total de empresas coletadas",
    ["source"],
)

COLLECTION_DURATION = Histogram(
    "collection_duration_seconds",
    "Duração das coletas",
    ["spider"],
)

COLLECTION_FAILURES = Counter(
    "collection_failures_total",
    "Total de falhas na coleta",
    ["spider", "error_type"],
)

DB_CONNECTIONS = Gauge(
    "db_connections_active",
    "Conexões ativas no banco",
)

ITEMS_IN_DB = Gauge(
    "items_in_db_total",
    "Total de itens no banco",
    ["table"],
)
