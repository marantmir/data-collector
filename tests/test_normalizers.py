from etl.normalizers import (
    normalize_cep,
    normalize_cnpj,
    normalize_phone,
    normalize_razao_social,
    remove_accents,
    slugify,
)


class TestNormalizers:
    def test_normalize_cnpj(self):
        assert normalize_cnpj("11.222.333/0001-81") == "11222333000181"
        assert normalize_cnpj("11222333000181") == "11222333000181"
        assert normalize_cnpj("") == "00000000000000"

    def test_normalize_phone(self):
        assert normalize_phone("(11) 99999-8888") == "11999998888"
        assert normalize_phone("+55 11 99999-8888") == "5511999998888"

    def test_normalize_cep(self):
        assert normalize_cep("01310-100") == "01310100"
        assert normalize_cep("01310100") == "01310100"

    def test_remove_accents(self):
        assert remove_accents("São Paulo") == "Sao Paulo"
        assert remove_accents("João") == "Joao"
        assert remove_accents("México") == "Mexico"

    def test_normalize_razao_social(self):
        assert normalize_razao_social("Empresa Exemplo Ltda") == "EMPRESA EXEMPLO LTDA"
        assert normalize_razao_social("João & Cia.") == "JOAO & CIA."

    def test_slugify(self):
        assert slugify("Empresa Exemplo Ltda") == "empresa-exemplo-ltda"
        assert slugify("São Paulo") == "sao-paulo"
        assert slugify("João & Cia.") == "joao-cia"
