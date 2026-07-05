import logging

import httpx

from sources.base import CompanyData, DataSourceConnector, PartnerData

logger = logging.getLogger(__name__)


class CNPJaConnector(DataSourceConnector):
    name = "cnpja"
    base_url = "https://api.cnpja.com.br"

    def __init__(self, api_key: str, timeout: int = 30):
        self.api_key = api_key
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Authorization": api_key},
        )

    def fetch_company(self, cnpj: str) -> CompanyData:
        cnpj_clean = self.normalize_cnpj(cnpj)
        response = self.client.get(f"/companies/{cnpj_clean}")
        response.raise_for_status()
        data = response.json()
        return self._parse_company(data)

    def fetch_partners(self, cnpj: str) -> list[PartnerData]:
        cnpj_clean = self.normalize_cnpj(cnpj)
        response = self.client.get(f"/companies/{cnpj_clean}")
        response.raise_for_status()
        data = response.json()
        return self._parse_partners(data)

    def _parse_company(self, data: dict) -> CompanyData:
        alias = data.get("alias", {}) or {}
        address = data.get("address", {}) or {}

        cnae_principal = None
        cnae_sec = []
        main_activity = data.get("mainActivity")
        if main_activity:
            cnae_principal = main_activity.get("code")
        for a in data.get("sideActivities", []):
            cnae_sec.append({"codigo": a.get("code"), "descricao": a.get("text")})

        endereco = {
            "logradouro": address.get("street"),
            "numero": address.get("number"),
            "complemento": address.get("details"),
            "bairro": address.get("district"),
            "cep": address.get("zip"),
            "cidade": address.get("city"),
            "uf": address.get("state"),
        }
        endereco = {k: v for k, v in endereco.items() if v is not None}

        company_data = data.get("company", {}) or {}
        natureza = company_data.get("legalNature")
        porte = company_data.get("size")
        situacao_raw = data.get("status", {}).get("text") if data.get("status") else None
        data_situacao = data.get("statusDate")

        return CompanyData(
            cnpj=self.normalize_cnpj(data.get("ein", {}).get("ein", "") if data.get("ein") else ""),
            razao_social=data.get("name", ""),
            nome_fantasia=alias.get("name") if alias else None,
            cnae_principal=cnae_principal,
            cnae_secundarias=cnae_sec or None,
            natureza_juridica=natureza,
            porte=porte,
            situacao_cadastral=situacao_raw,
            data_situacao=data_situacao,
            capital_social=data.get("capital"),
            endereco=endereco or None,
            socios=self._parse_partners(data),
            raw=data,
        )

    def _parse_partners(self, data: dict) -> list[PartnerData]:
        socios = []
        for m in data.get("members", []):
            person = m.get("person", {}) or {}
            socios.append(
                PartnerData(
                    cpf_cnpj=person.get("ein", {}).get("ein") if person.get("ein") else None,
                    nome=person.get("name", {}).get("full") if person.get("name") else None,
                    qualificacao=m.get("role", {}).get("text") if m.get("role") else None,
                    percentual=m.get("share"),
                    data_entrada=m.get("since"),
                )
            )
        return socios
