import pytest
from pydantic import ValidationError

from etl.validators import (
    BidValidator,
    CompanyValidator,
    FinancialValidator,
    sanitize_cnpj,
    validate_cnpj,
)


class TestCNPJ:
    def test_sanitize(self):
        assert sanitize_cnpj("11.222.333/0001-81") == "11222333000181"
        assert sanitize_cnpj("11.222.333/0001-81") == "11222333000181"

    def test_validate_valid(self):
        assert validate_cnpj("11.222.333/0001-81") is True

    def test_validate_invalid(self):
        assert validate_cnpj("00.000.000/0000-00") is False
        assert validate_cnpj("11.111.111/1111-11") is False
        assert validate_cnpj("12.345.678/0001-00") is False

    def test_validate_wrong_length(self):
        assert validate_cnpj("123") is False
        assert validate_cnpj("") is False


class TestCompanyValidator:
    def test_valid_company(self):
        data = {
            "cnpj": "11.222.333/0001-81",
            "razao_social": "Empresa Exemplo Ltda",
        }
        v = CompanyValidator(**data)
        assert v.cnpj == "11222333000181"

    def test_invalid_cnpj_raises(self):
        with pytest.raises(ValidationError):
            CompanyValidator(cnpj="00.000.000/0000-00", razao_social="Teste")

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            CompanyValidator()

    def test_optional_fields(self):
        data = {
            "cnpj": "11.222.333/0001-81",
            "razao_social": "Empresa Exemplo Ltda",
            "nome_fantasia": "Exemplo",
            "porte": "ME",
            "capital_social": 50000.00,
            "endereco": {"cidade": "São Paulo", "uf": "SP"},
            "contato": {"email": "contato@exemplo.com"},
        }
        v = CompanyValidator(**data)
        assert v.nome_fantasia == "Exemplo"
        assert v.capital_social == 50000.00


class TestFinancialValidator:
    def test_valid_balanco(self):
        data = {
            "company_cnpj": "11222333000181",
            "tipo": "BALANCO",
            "ano_exercicio": 2025,
            "data_referencia": "2025-12-31",
            "valores": {"ativo_total": 1_000_000, "passivo_total": 600_000},
        }
        v = FinancialValidator(**data)
        assert v.tipo == "BALANCO"
        assert v.moeda == "BRL"

    def test_invalid_tipo(self):
        with pytest.raises(ValidationError):
            FinancialValidator(
                company_cnpj="11222333000181",
                tipo="INVALIDO",
                ano_exercicio=2025,
                data_referencia="2025-12-31",
                valores={},
            )

    def test_trimestre_validation(self):
        with pytest.raises(ValidationError):
            FinancialValidator(
                company_cnpj="11222333000181",
                tipo="DRE",
                ano_exercicio=2025,
                trimestre=5,
                data_referencia="2025-12-31",
                valores={},
            )


class TestBidValidator:
    def test_valid_bid(self):
        data = {
            "orgao_responsavel": "Prefeitura Municipal",
            "numero_licitacao": "001/2025",
            "modalidade": "Pregão",
            "valor_estimado": 500000.00,
        }
        v = BidValidator(**data)
        assert v.orgao_responsavel == "Prefeitura Municipal"

    def test_missing_required(self):
        with pytest.raises(ValidationError):
            BidValidator()
