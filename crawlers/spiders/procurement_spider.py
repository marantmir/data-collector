from typing import Any

import scrapy
from scrapy.http import Response

from crawlers.items import BidItem
from crawlers.spiders.base_spider import BaseBusinessSpider


class ProcurementSpider(BaseBusinessSpider):
    name = "procurement"
    allowed_domains: list[str] = []

    def start_requests(self) -> Any:
        yield scrapy.Request(
            url="https://exemplo-api.app/api/licitacoes",
            callback=self.parse_bid_list,
        )

    def parse_bid_list(self, response: Response) -> Any:
        data = response.json()
        for bid in data.get("licitacoes", []):
            yield scrapy.Request(
                url=bid.get("url_detalhe"),
                callback=self.parse_bid_detail,
                meta={"bid": bid},
            )
        next_page = data.get("next")
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_bid_list)

    def parse_bid_detail(self, response: Response) -> Any:
        bid = response.meta["bid"]
        yield BidItem(
            orgao_responsavel=bid.get("orgao"),
            modalidade=bid.get("modalidade"),
            numero_licitacao=bid.get("numero"),
            objeto=bid.get("objeto"),
            valor_estimado=bid.get("valor_estimado"),
            data_abertura=bid.get("data_abertura"),
            situacao=bid.get("situacao"),
            source_url=response.url,
            source_id=self.source_id,
        )

    def parse(self, response: Response, **kwargs: Any) -> Any:
        pass
