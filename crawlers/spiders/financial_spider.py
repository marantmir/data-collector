from typing import Any

import scrapy
from scrapy.http import Response

from crawlers.items import FinancialItem
from crawlers.spiders.base_spider import BaseBusinessSpider


class FinancialSpider(BaseBusinessSpider):
    name = "financial"
    allowed_domains: list[str] = []

    def __init__(self, cnpjs: str | None = None, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.cnpjs = cnpjs.split(",") if cnpjs else []

    def start_requests(self) -> Any:
        for cnpj in self.cnpjs:
            cnpj_clean = cnpj.strip().replace(".", "").replace("/", "").replace("-", "")
            yield scrapy.Request(
                url=f"https://exemplo-api.app/api/demonstrativos/{cnpj_clean}",
                callback=self.parse_financial,
                meta={"cnpj": cnpj_clean},
            )

    def parse_financial(self, response: Response) -> Any:
        data = response.json()
        for stmt in data.get("demonstrativos", []):
            yield FinancialItem(
                company_cnpj=response.meta["cnpj"],
                tipo=stmt.get("tipo"),
                ano_exercicio=stmt.get("ano_exercicio"),
                trimestre=stmt.get("trimestre"),
                data_referencia=stmt.get("data_referencia"),
                valores=stmt.get("valores"),
                moeda=stmt.get("moeda", "BRL"),
                audited=stmt.get("audited", False),
                source_url=response.url,
                source_id=self.source_id,
            )

    def parse(self, response: Response, **kwargs: Any) -> Any:
        pass
