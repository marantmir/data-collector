from sources.cache import _key


class TestCacheKey:
    def test_key_generation(self):
        assert _key("11222333000181") == "cnpj:11222333000181"

    def test_key_with_formatting(self):
        assert _key("11.222.333/0001-81") == "cnpj:11222333000181"

    def test_key_with_custom_prefix(self):
        assert _key("11222333000181", prefix="test") == "test:11222333000181"
