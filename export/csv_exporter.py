import csv
import io
from typing import Any

from db.models.company import Company
from export.base import BaseExporter


class CSVExporter(BaseExporter):
    format = "csv"

    HEADERS = [
        "cnpj", "razao_social", "nome_fantasia", "cnae_principal", "porte",
        "situacao_cadastral", "natureza_juridica", "regime_tributario",
        "capital_social", "logradouro", "numero", "bairro", "cidade", "uf",
        "cep", "telefone", "email",
    ]

    def export_companies(self, companies: list[Company], **kwargs: Any) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.HEADERS)
        for c in companies:
            writer.writerow(self._row(c))
        return output.getvalue()

    def export_company(self, company: Company, **kwargs: Any) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.HEADERS)
        writer.writerow(self._row(company))
        return output.getvalue()

    def _row(self, c: Company) -> list:
        end = c.endereco or {}
        contato = c.contato or {}
        return [
            self._format_cnpj(c.cnpj) if c.cnpj else "",
            c.razao_social or "",
            c.nome_fantasia or "",
            c.cnae_principal or "",
            c.porte or "",
            c.situacao_cadastral or "",
            c.natureza_juridica or "",
            c.regime_tributario or "",
            str(c.capital_social or ""),
            end.get("logradouro", ""),
            end.get("numero", ""),
            end.get("bairro", ""),
            end.get("cidade", ""),
            end.get("uf", ""),
            end.get("cep", ""),
            contato.get("telefone", ""),
            contato.get("email", ""),
        ]
