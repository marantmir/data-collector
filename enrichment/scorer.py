from dataclasses import dataclass


@dataclass
class SourceReliability:
    name: str
    base_score: float
    fields_expected: list[str]


SOURCES_CONFIG = [
    SourceReliability("brasilapi", 0.9, ["razao_social", "cnpj", "cnae_fiscal"]),
    SourceReliability("cnpja", 0.85, ["name", "ein"]),
]


class ReliabilityScorer:
    def score_source(self, source_name: str, data) -> float:
        config = next((s for s in SOURCES_CONFIG if s.name == source_name), None)
        if not config:
            return 0.0

        raw = data.raw if hasattr(data, "raw") and data.raw else {}
        filled = sum(1 for f in config.fields_expected if raw.get(f))
        ratio = filled / len(config.fields_expected)

        completeness = 0.0
        if data.razao_social:
            completeness += 0.3
        if data.cnpj:
            completeness += 0.2
        if data.cnae_principal:
            completeness += 0.15
        if data.endereco:
            completeness += 0.15
        if data.socios:
            completeness += 0.1
        if data.contato and (data.contato.get("telefone") or data.contato.get("email")):
            completeness += 0.1

        return config.base_score * ratio * completeness
