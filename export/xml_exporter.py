from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring

from db.models.company import Company
from export.base import BaseExporter


class XMLExporter(BaseExporter):
    format = "xml"

    def export_companies(self, companies: list[Company], **kwargs: Any) -> str:
        root = Element("empresas")
        for c in companies:
            root.append(self._build(c))
        return tostring(root, encoding="unicode", xml_declaration=True)

    def export_company(self, company: Company, **kwargs: Any) -> str:
        root = Element("empresa")
        root.append(self._build(company))
        return tostring(root, encoding="unicode", xml_declaration=True)

    def _build(self, c: Company) -> Element:
        e = Element("empresa")
        SubElement(e, "cnpj").text = self._format_cnpj(c.cnpj) if c.cnpj else ""
        SubElement(e, "razao_social").text = c.razao_social or ""
        SubElement(e, "nome_fantasia").text = c.nome_fantasia or ""
        SubElement(e, "cnae_principal").text = c.cnae_principal or ""
        SubElement(e, "porte").text = c.porte or ""
        SubElement(e, "situacao_cadastral").text = c.situacao_cadastral or ""
        SubElement(e, "natureza_juridica").text = c.natureza_juridica or ""
        SubElement(e, "regime_tributario").text = c.regime_tributario or ""
        SubElement(e, "capital_social").text = str(c.capital_social or "")

        end = c.endereco or {}
        addr = SubElement(e, "endereco")
        SubElement(addr, "logradouro").text = end.get("logradouro", "")
        SubElement(addr, "numero").text = end.get("numero", "")
        SubElement(addr, "bairro").text = end.get("bairro", "")
        SubElement(addr, "cidade").text = end.get("cidade", "")
        SubElement(addr, "uf").text = end.get("uf", "")
        SubElement(addr, "cep").text = end.get("cep", "")

        ct = c.contato or {}
        cont = SubElement(e, "contato")
        SubElement(cont, "telefone").text = ct.get("telefone", "")
        SubElement(cont, "email").text = ct.get("email", "")

        if c.partners:
            socios = SubElement(e, "socios")
            for p in c.partners:
                s = SubElement(socios, "socio")
                SubElement(s, "nome").text = p.nome or ""
                SubElement(s, "cpf_cnpj").text = p.cpf_cnpj or ""
                SubElement(s, "qualificacao").text = p.qualificacao or ""

        return e
