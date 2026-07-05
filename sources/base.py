from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class CompanyData:
    cnpj: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    cnae_principal: Optional[str] = None
    cnae_secundarias: Optional[list[dict]] = None
    natureza_juridica: Optional[str] = None
    porte: Optional[str] = None
    situacao_cadastral: Optional[str] = None
    data_situacao: Optional[str] = None
    regime_tributario: Optional[str] = None
    capital_social: Optional[float] = None
    endereco: Optional[dict] = None
    contato: Optional[dict] = None
    socios: list[dict] = field(default_factory=list)
    raw: Optional[dict] = None


@dataclass
class PartnerData:
    cpf_cnpj: Optional[str] = None
    nome: Optional[str] = None
    qualificacao: Optional[str] = None
    percentual: Optional[float] = None
    data_entrada: Optional[str] = None


class DataSourceConnector(ABC):
    name: str = "base"

    @abstractmethod
    def fetch_company(self, cnpj: str) -> CompanyData:
        ...

    @abstractmethod
    def fetch_partners(self, cnpj: str) -> list[PartnerData]:
        ...

    def normalize_cnpj(self, cnpj: str) -> str:
        import re
        return re.sub(r"\D", "", cnpj).zfill(14)
