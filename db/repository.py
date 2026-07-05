import uuid
from typing import Optional

from sqlalchemy.orm import Session

from db.models.company import Company
from db.models.financial import FinancialStatement
from db.models.partner import Partner
from db.models.procurement import ProcurementBid


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_cnpj(self, cnpj: str) -> Optional[Company]:
        return self.db.query(Company).filter(Company.cnpj == cnpj).first()

    def get_by_id(self, company_id: uuid.UUID) -> Optional[Company]:
        return self.db.query(Company).filter(Company.id == company_id).first()

    def list(self, skip: int = 0, limit: int = 100, **filters) -> list[Company]:
        q = self.db.query(Company)
        for key, value in filters.items():
            if hasattr(Company, key) and value is not None:
                q = q.filter(getattr(Company, key) == value)
        return q.offset(skip).limit(limit).all()

    def upsert(self, data: dict) -> Company:
        company = self.get_by_cnpj(data["cnpj"])
        if company:
            for key, value in data.items():
                if value is not None:
                    setattr(company, key, value)
        else:
            company = Company(**data)
            self.db.add(company)
        self.db.flush()
        return company

    def count(self, **filters) -> int:
        q = self.db.query(Company)
        for key, value in filters.items():
            if hasattr(Company, key) and value is not None:
                q = q.filter(getattr(Company, key) == value)
        return q.count()


class PartnerRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, data: dict) -> Partner:
        partner = (
            self.db.query(Partner)
            .filter(
                Partner.company_id == data["company_id"],
                Partner.cpf_cnpj == data.get("cpf_cnpj"),
            )
            .first()
        )
        if partner:
            for key, value in data.items():
                if value is not None:
                    setattr(partner, key, value)
        else:
            partner = Partner(**data)
            self.db.add(partner)
        self.db.flush()
        return partner


class FinancialRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, data: dict) -> FinancialStatement:
        stmt = (
            self.db.query(FinancialStatement)
            .filter(
                FinancialStatement.company_id == data["company_id"],
                FinancialStatement.tipo == data["tipo"],
                FinancialStatement.ano_exercicio == data["ano_exercicio"],
                FinancialStatement.trimestre == data.get("trimestre"),
            )
            .first()
        )
        if stmt:
            for key, value in data.items():
                if value is not None:
                    setattr(stmt, key, value)
        else:
            stmt = FinancialStatement(**data)
            self.db.add(stmt)
        self.db.flush()
        return stmt


class BidRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, data: dict) -> ProcurementBid:
        bid = (
            self.db.query(ProcurementBid)
            .filter(
                ProcurementBid.orgao_responsavel == data["orgao_responsavel"],
                ProcurementBid.numero_licitacao == data["numero_licitacao"],
            )
            .first()
        )
        if bid:
            for key, value in data.items():
                if value is not None:
                    setattr(bid, key, value)
        else:
            bid = ProcurementBid(**data)
            self.db.add(bid)
        self.db.flush()
        return bid
