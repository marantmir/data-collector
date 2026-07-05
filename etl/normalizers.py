import re
import unicodedata


def normalize_cnpj(value: str) -> str:
    return re.sub(r"\D", "", value).zfill(14)


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", value)


def normalize_cep(value: str) -> str:
    return re.sub(r"\D", "", value).zfill(8)


def remove_accents(value: str) -> str:
    nfkd = unicodedata.normalize("NFKD", value)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalize_razao_social(value: str) -> str:
    return remove_accents(value.strip().upper())


def slugify(value: str) -> str:
    value = remove_accents(value).lower().strip()
    value = re.sub(r"[^\w\s-]", "", value)
    return re.sub(r"[-\s]+", "-", value)
