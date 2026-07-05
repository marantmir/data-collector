import re
from difflib import SequenceMatcher
from typing import Optional

from sqlalchemy.orm import Session

from db.models.company import Company
from etl.normalizers import normalize_razao_social


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def normalize_for_comparison(value: str) -> str:
    value = normalize_razao_social(value)
    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\b(LTDA|ME|EPP|S/A|SA|EIRELI)\b", "", value)
    return value.strip()


def find_duplicate_cnpj(db: Session, cnpj: str) -> Optional[Company]:
    return db.query(Company).filter(Company.cnpj == cnpj).first()


def find_duplicate_name(
    db: Session, razao_social: str, threshold: float = 0.85
) -> list[Company]:
    normalized = normalize_for_comparison(razao_social)
    candidates = db.query(Company).all()
    matches = []
    for company in candidates:
        candidate_norm = normalize_for_comparison(company.razao_social)
        score = similarity(normalized, candidate_norm)
        if score >= threshold:
            matches.append((company, score))
    return sorted(matches, key=lambda x: -x[1])
