import pytest

from sources import get_connector
from sources.base import CompanyData, PartnerData


class TestBrasilAPIConnector:
    def test_fetch_real_company(self):
        conn = get_connector("brasilapi")
        data = conn.fetch_company("19131243000197")
        assert isinstance(data, CompanyData)
        assert data.cnpj == "19131243000197"
        assert data.razao_social == "OPEN KNOWLEDGE BRASIL"
        assert data.situacao_cadastral == "ATIVA"
        assert data.endereco is not None
        assert "logradouro" in data.endereco

    def test_fetch_partners_real(self):
        conn = get_connector("brasilapi")
        partners = conn.fetch_partners("19131243000197")
        assert len(partners) > 0
        assert all(isinstance(p, PartnerData) for p in partners)
        assert any(p.nome for p in partners)

    def test_fetch_company_full_structure(self):
        conn = get_connector("brasilapi")
        data = conn.fetch_company("33000167000101")
        assert data.cnae_principal == "600001"
        assert data.porte == "Demais"
        assert data.natureza_juridica is not None
        assert data.capital_social is not None and data.capital_social > 0

    def test_parse_partner_from_company(self):
        conn = get_connector("brasilapi")
        data = conn.fetch_company("33000167000101")
        assert len(data.socios) > 0
        socio = data.socios[0]
        assert socio.nome is not None
        assert socio.qualificacao is not None

    def test_connector_registry(self):
        conn = get_connector("brasilapi")
        assert conn.name == "brasilapi"

    def test_invalid_connector_raises(self):
        with pytest.raises(ValueError):
            get_connector("invalid_source")


class TestCompanyData:
    def test_defaults(self):
        data = CompanyData(cnpj="11222333000181", razao_social="Teste")
        assert data.nome_fantasia is None
        assert data.socios == []
        assert data.capital_social is None

    def test_with_socios(self):
        data = CompanyData(
            cnpj="11222333000181",
            razao_social="Teste",
            socios=[PartnerData(nome="João", qualificacao="Sócio")],
        )
        assert len(data.socios) == 1
        assert data.socios[0].nome == "João"
