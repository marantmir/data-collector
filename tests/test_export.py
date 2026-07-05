from uuid import uuid4

from db.models.company import Company
from export import get_exporter


def make_company(**overrides) -> Company:
    c = Company(
        id=uuid4(),
        cnpj="11222333000181",
        razao_social="Empresa Exemplo Ltda",
        nome_fantasia="Exemplo",
        cnae_principal="6202300",
        porte="Demais",
        situacao_cadastral="Ativa",
        natureza_juridica="Sociedade Empresária Limitada",
        capital_social=100000.00,
        endereco={
            "logradouro": "Rua Exemplo",
            "numero": "100",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01001000",
        },
        contato={"telefone": "11999998888", "email": "contato@exemplo.com"},
    )
    for k, v in overrides.items():
        setattr(c, k, v)
    return c


class TestCSVExport:
    def test_export_single_company(self):
        exp = get_exporter("csv")
        c = make_company()
        result = exp.export_company(c)
        assert c.razao_social in result
        assert "11.222.333/0001-81" in result
        assert result.startswith("cnpj")

    def test_export_multiple_companies(self):
        exp = get_exporter("csv")
        companies = [make_company(), make_company(cnpj="33000167000101", razao_social="Petrobras")]
        result = exp.export_companies(companies)
        lines = result.strip().split("\n")
        assert len(lines) == 3
        assert "Petrobras" in result


class TestXMLExport:
    def test_export_single_company(self):
        exp = get_exporter("xml")
        c = make_company()
        result = exp.export_company(c)
        assert "<empresa>" in result
        assert c.razao_social in result
        assert "<cnpj>" in result

    def test_export_includes_partners(self):
        from db.models.partner import Partner

        exp = get_exporter("xml")
        c = make_company()
        c.partners = [
            Partner(id=uuid4(), company_id=c.id, nome="João", qualificacao="Sócio"),
        ]
        result = exp.export_company(c)
        assert "João" in result
        assert "<socios>" in result


class TestSPEDExport:
    def test_export_single_company(self):
        exp = get_exporter("sped")
        c = make_company()
        result = exp.export_company(c)
        assert "0001|" in result
        assert "11.222.333/0001-81" in result
        assert c.razao_social in result

    def test_export_format_pipe_separated(self):
        exp = get_exporter("sped")
        c = make_company()
        result = exp.export_company(c)
        fields = result.split("|")
        assert fields[0] == "0001"
        assert fields[2] == c.razao_social
