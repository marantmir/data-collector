from typing import Any

import scrapy
from scrapy.http import Response

from crawlers.items import CompanyItem, PartnerItem
from crawlers.spiders.base_spider import BaseBusinessSpider
from sources import get_connector


class CadastralSpider(BaseBusinessSpider):
    name = "cadastral"
    allowed_domains = ["brasilapi.com.br", "api.cnpja.com.br"]

    def __init__(self, cnpjs: str | None = None, source: str = "brasilapi", **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.cnpjs = cnpjs.split(",") if cnpjs else []
        self.connector = get_connector(source)

    def start_requests(self) -> Any:
        for cnpj in self.cnpjs:
            cnpj_clean = cnpj.strip()
            yield scrapy.Request(
                url="https://brasilapi.com.br/api/cnpj/v1/" + cnpj_clean,
                callback=self.parse_company,
                meta={"cnpj": cnpj_clean, "api": "brasilapi"},
                errback=self._handle_fallback,
            )

    def parse_company(self, response: Response) -> Any:
        data = response.json()
        company = self.connector._parse_company(data)
        yield CompanyItem(
            cnpj=company.cnpj,
            razao_social=company.razao_social,
            nome_fantasia=company.nome_fantasia,
            cnae_principal=company.cnae_principal,
            cnae_secundarias=company.cnae_secundarias,
            natureza_juridica=company.natureza_juridica,
            porte=company.porte,
            situacao_cadastral=company.situacao_cadastral,
            data_situacao=company.data_situacao,
            regime_tributario=company.regime_tributario,
            capital_social=company.capital_social,
            endereco=company.endereco,
            contato=company.contato,
            source_id=self.source_id,
        )
        for socio in company.socios:
            yield PartnerItem(
                company_cnpj=company.cnpj,
                cpf_cnpj=socio.cpf_cnpj,
                nome=socio.nome,
                qualificacao=socio.qualificacao,
                percentual=socio.percentual,
                source_id=self.source_id,
            )

    def _handle_fallback(self, failure: Any) -> Any:
        cnpj = failure.request.meta["cnpj"]
        self.logger.warning(f"Falha BrasilAPI para {cnpj}, tentando CNPJa...")
        try:
            from config import settings
            from sources.cnpja import CNPJaConnector

            fallback = CNPJaConnector(api_key=getattr(settings, "cnpja_api_key", ""))
            company = fallback.fetch_company(cnpj)
            yield CompanyItem(
                cnpj=company.cnpj,
                razao_social=company.razao_social,
                nome_fantasia=company.nome_fantasia,
                cnae_principal=company.cnae_principal,
                cnae_secundarias=company.cnae_secundarias,
                natureza_juridica=company.natureza_juridica,
                porte=company.porte,
                situacao_cadastral=company.situacao_cadastral,
                capital_social=company.capital_social,
                endereco=company.endereco,
                contato=company.contato,
                source_id=self.source_id,
            )
        except Exception as e:
            self.logger.error(f"Fallback CNPJa também falhou para {cnpj}: {e}")

    def parse(self, response: Response, **kwargs: Any) -> Any:
        pass
