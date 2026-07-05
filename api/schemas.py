from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class CompanyResponse(BaseModel):
    id: UUID
    cnpj: str
    razao_social: str
    nome_fantasia: str | None = None
    cnae_principal: str | None = None
    cnae_secundarias: dict | None = None
    natureza_juridica: str | None = None
    porte: str | None = None
    situacao_cadastral: str | None = None
    regime_tributario: str | None = None
    capital_social: Decimal | None = None
    endereco: dict | None = None
    contato: dict | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CompanyListResponse(BaseModel):
    items: list[CompanyResponse]
    total: int
    skip: int
    limit: int


class FinancialResponse(BaseModel):
    id: UUID
    company_id: UUID
    tipo: str
    ano_exercicio: int
    trimestre: int | None = None
    data_referencia: str
    valores: dict
    moeda: str
    audited: bool

    model_config = {"from_attributes": True}


class BidResponse(BaseModel):
    id: UUID
    orgao_responsavel: str | None = None
    modalidade: str | None = None
    numero_licitacao: str | None = None
    objeto: str | None = None
    valor_estimado: Decimal | None = None
    situacao: str | None = None

    model_config = {"from_attributes": True}
