from fastapi import Depends
from sqlalchemy.orm import Session

from db.session import get_db as _get_db

get_db = _get_db


def get_company_repo(db: Session = Depends(get_db)):
    from db.repository import CompanyRepository
    return CompanyRepository(db)


def get_financial_repo(db: Session = Depends(get_db)):
    from db.repository import FinancialRepository
    return FinancialRepository(db)
