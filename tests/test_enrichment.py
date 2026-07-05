from enrichment.scorer import ReliabilityScorer


class FakeCompanyData:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        if not hasattr(self, "raw"):
            self.raw = {}


class TestReliabilityScorer:
    def setup_method(self):
        self.scorer = ReliabilityScorer()

    def test_score_brasilapi_full(self):
        data = FakeCompanyData(
            razao_social="Teste",
            cnpj="11222333000181",
            cnae_principal="6202300",
            endereco={"cidade": "SP"},
            socios=[{"nome": "João"}],
            contato={"telefone": "11999998888"},
            raw={"razao_social": "Teste", "cnpj": "11222333000181", "cnae_fiscal": "6202300"},
        )
        score = self.scorer.score_source("brasilapi", data)
        assert 0 < score <= 1.0

    def test_score_brasilapi_empty(self):
        data = FakeCompanyData(
            razao_social="",
            cnpj="",
            cnae_principal=None,
            endereco=None,
            socios=[],
            contato={},
            raw={},
        )
        score = self.scorer.score_source("brasilapi", data)
        assert score == 0.0

    def test_score_unknown_source(self):
        data = FakeCompanyData(razao_social="Teste")
        score = self.scorer.score_source("unknown", data)
        assert score == 0.0
