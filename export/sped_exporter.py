from typing import Any

from db.models.company import Company
from export.base import BaseExporter


class SPEDExporter(BaseExporter):
    format = "sped"

    def export_companies(self, companies: list[Company], **kwargs: Any) -> str:
        lines = [
            "REGISTRO|CNPJ|RAZAO_SOCIAL|NOME_FANTASIA|CNAE|PORTE|SITUACAO|NATUREZA_JURIDICA|REGIME_TRIB|CAPITAL_SOCIAL|CIDADE|UF",
        ]
        for c in companies:
            lines.append(self._line(c))
        return "\n".join(lines)

    def export_company(self, company: Company, **kwargs: Any) -> str:
        return self._line(company)

    def _line(self, c: Company) -> str:
        end = c.endereco or {}
        return "|".join([
            "0001",
            self._format_cnpj(c.cnpj) if c.cnpj else "",
            c.razao_social or "",
            c.nome_fantasia or "",
            c.cnae_principal or "",
            c.porte or "",
            c.situacao_cadastral or "",
            c.natureza_juridica or "",
            c.regime_tributario or "",
            str(c.capital_social or ""),
            end.get("cidade", ""),
            end.get("uf", ""),
        ])
