from etl.deduplicator import normalize_for_comparison, similarity


class TestDeduplicator:
    def test_similarity_identical(self):
        assert similarity("Empresa Exemplo Ltda", "Empresa Exemplo Ltda") == 1.0

    def test_similarity_different(self):
        assert similarity("ABC Ltda", "XYZ S/A") < 0.5

    def test_similarity_similar(self):
        score = similarity("Empresa Exemplo Ltda", "Empresa Exemplo ME")
        assert 0.6 < score < 1.0

    def test_normalize_for_comparison_removes_suffixes(self):
        result = normalize_for_comparison("Empresa Exemplo Ltda")
        assert "LTDA" not in result

    def test_normalize_for_comparison(self):
        a = normalize_for_comparison("Empresa Exemplo Ltda")
        b = normalize_for_comparison("Empresa Exemplo ME")
        assert a == b
