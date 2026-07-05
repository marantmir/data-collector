import re
from typing import Any

from pydantic import BaseModel, Field, field_validator


def sanitize_cnpj(cnpj: str) -> str:
    return re.sub(r"\D", "", cnpj)


def validate_cnpj(cnpj: str) -> bool:
    cnpj = sanitize_cnpj(cnpj)
    if len(cnpj) != 14 or cnpj in (c * 14 for c in "0123456789"):
        return False

    def calc_digit(digits: str, weights: list[int]) -> int:
        s = sum(int(d) * w for d, w in zip(digits, weights))
        r = s % 11
        return 0 if r < 2 else 11 - r

    if calc_digit(cnpj[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]) != int(cnpj[12]):
        return False
    if calc_digit(cnpj[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]) != int(cnpj[13]):
        return False
    return True


class CompanyValidator(BaseModel):
    cnpj: str = Field(..., min_length=14, max_length=18)
    razao_social: str = Field(..., min_length=1, max_length=255)
    nome_fantasia: str | None = None
    cnae_principal: str | None = Field(None, pattern=r"^\d{4,7}$")
    cnae_secundarias: list[str] | None = None
    natureza_juridica: str | None = None
    porte: str | None = None
    situacao_cadastral: str | None = None
    capital_social: float | None = None
    endereco: dict | None = None
    contato: dict | None = None

    @field_validator("cnpj")
    @classmethod
    def check_cnpj(cls, v: str) -> str:
        cleaned = sanitize_cnpj(v)
        if not validate_cnpj(cleaned):
            raise ValueError(f"CNPJ inválido: {v}")
        return cleaned


class FinancialValidator(BaseModel):
    company_cnpj: str = Field(..., min_length=14)
    tipo: str = Field(..., pattern=r"^(BALANCO|DRE|FLUXO_CAIXA)$")
    ano_exercicio: int = Field(..., ge=2000, le=2100)
    trimestre: int | None = Field(None, ge=1, le=4)
    data_referencia: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    valores: dict[str, Any]
    moeda: str = "BRL"
    audited: bool = False
    source_url: str | None = None


class BidValidator(BaseModel):
    orgao_responsavel: str = Field(..., min_length=1)
    modalidade: str | None = None
    numero_licitacao: str = Field(..., min_length=1)
    objeto: str | None = None
    valor_estimado: float | None = None
    data_abertura: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    data_resultado: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    situacao: str | None = None
    source_url: str | None = None
