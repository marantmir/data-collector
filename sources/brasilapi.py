import logging

import httpx

from sources.base import CompanyData, DataSourceConnector, PartnerData
from sources.cache import get_cached, set_cached

logger = logging.getLogger(__name__)

REGIME_MAP = {
    1: "Simples Nacional",
    2: "Simples Nacional - MEI",
    3: "Lucro Presumido",
    4: "Lucro Real",
}


class BrasilAPIConnector(DataSourceConnector):
    name = "brasilapi"
    base_url = "https://brasilapi.com.br/api"

    def __init__(self, timeout: int = 30):
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def fetch_company(self, cnpj: str) -> CompanyData:
        cnpj_clean = self.normalize_cnpj(cnpj)

        cached = get_cached(cnpj_clean)
        if cached:
            return self._parse_company(cached)

        response = self.client.get(f"/cnpj/v1/{cnpj_clean}")
        response.raise_for_status()
        data = response.json()
        set_cached(cnpj_clean, data)
        return self._parse_company(data)

    def fetch_partners(self, cnpj: str) -> list[PartnerData]:
        cnpj_clean = self.normalize_cnpj(cnpj)

        cached = get_cached(cnpj_clean)
        if cached:
            return self._parse_partners(cached)

        response = self.client.get(f"/cnpj/v1/{cnpj_clean}")
        response.raise_for_status()
        data = response.json()
        set_cached(cnpj_clean, data)
        return self._parse_partners(data)

    def _parse_company(self, data: dict) -> CompanyData:
        cnae_sec = []
        for c in data.get("cnae_secundarias", []):
            cnae_sec.append({"codigo": c.get("codigo"), "descricao": c.get("descricao")})

        endereco = {
            "logradouro": data.get("logradouro"),
            "numero": data.get("numero"),
            "complemento": data.get("complemento"),
            "bairro": data.get("bairro"),
            "cep": data.get("cep"),
            "cidade": data.get("municipio"),
            "uf": data.get("uf"),
        }
        endereco = {k: v for k, v in endereco.items() if v is not None}

        contato = {}
        if data.get("ddd_telefone_1"):
            contato["telefone"] = data["ddd_telefone_1"]
        if data.get("email"):
            contato["email"] = data["email"]

        porte = data.get("porte", "").capitalize() if data.get("porte") else None

        if data.get("opcao_pelo_simples") is True:
            if data.get("opcao_pelo_mei") is True:
                regime = "Simples Nacional - MEI"
            else:
                regime = "Simples Nacional"
        else:
            regime = None

        situacao = data.get("descricao_situacao_cadastral")
        data_situacao = data.get("data_situacao_cadastral")

        return CompanyData(
            cnpj=self.normalize_cnpj(data.get("cnpj", "")),
            razao_social=data.get("razao_social", ""),
            nome_fantasia=data.get("nome_fantasia"),
            cnae_principal=str(data.get("cnae_fiscal")) if data.get("cnae_fiscal") is not None else None,
            cnae_secundarias=cnae_sec or None,
            natureza_juridica=data.get("natureza_juridica"),
            porte=porte,
            situacao_cadastral=situacao,
            data_situacao=data_situacao,
            regime_tributario=regime,
            capital_social=data.get("capital_social"),
            endereco=endereco or None,
            contato=contato or None,
            socios=self._parse_partners(data),
            raw=data,
        )

    def _parse_partners(self, data: dict) -> list[PartnerData]:
        socios = []
        for s in data.get("qsa", []):
            socios.append(
                PartnerData(
                    cpf_cnpj=s.get("cnpj_cpf_do_socio"),
                    nome=s.get("nome_socio"),
                    qualificacao=s.get("qualificacao_socio"),
                )
            )
        return socios
