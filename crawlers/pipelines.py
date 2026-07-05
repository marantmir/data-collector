import uuid
from datetime import datetime, timezone
from typing import Any

from itemadapter import ItemAdapter
from scrapy import Spider
from sqlalchemy.orm import Session

from crawlers.items import CompanyItem, FinancialItem, PartnerItem
from db.models.audit import AuditLog, CollectionJob
from db.models.company import Company
from db.models.financial import FinancialStatement
from db.models.partner import Partner
from db.session import SessionLocal


class DatabasePipeline:
    def open_spider(self, spider: Spider) -> None:
        self.session: Session = SessionLocal()
        self.job = CollectionJob(
            id=uuid.uuid4(),
            spider_name=spider.name,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        self.session.add(self.job)
        self.session.commit()

    def close_spider(self, spider: Spider) -> None:
        self.job.finished_at = datetime.now(timezone.utc)
        self.session.commit()
        self.session.close()

    def process_item(self, item: Any, spider: Spider) -> Any:
        adapter = ItemAdapter(item)
        data = adapter.asdict()

        if isinstance(item, CompanyItem):
            self._process_company(data)
        elif isinstance(item, PartnerItem):
            self._process_partner(data)
        elif isinstance(item, FinancialItem):
            self._process_financial(data)

        self.job.items_collected += 1
        self.session.commit()
        return item

    def _process_company(self, data: dict) -> Company:
        cnpj = data.pop("cnpj", "")
        existing = self.session.query(Company).filter(Company.cnpj == cnpj).first()
        if existing:
            old = {c.name: getattr(existing, c.name) for c in existing.__table__.columns}
            for key, value in data.items():
                if value is not None:
                    setattr(existing, key, value)
            self._log_audit("companies", existing.id, "UPDATE", old, data)
            return existing
        company = Company(cnpj=cnpj, **{k: v for k, v in data.items() if v is not None})
        self.session.add(company)
        self.session.flush()
        self._log_audit("companies", company.id, "INSERT", None, data)
        return company

    def _process_partner(self, data: dict) -> Partner:
        company = self.session.query(Company).filter(Company.cnpj == data["company_cnpj"]).first()
        if not company:
            return None
        data["company_id"] = company.id
        data.pop("company_cnpj", None)
        partner = (
            self.session.query(Partner)
            .filter(Partner.company_id == company.id, Partner.cpf_cnpj == data.get("cpf_cnpj"))
            .first()
        )
        if partner:
            for key, value in data.items():
                if value is not None:
                    setattr(partner, key, value)
        else:
            partner = Partner(**{k: v for k, v in data.items() if v is not None})
            self.session.add(partner)
        return partner

    def _process_financial(self, data: dict) -> FinancialStatement:
        company = self.session.query(Company).filter(Company.cnpj == data["company_cnpj"]).first()
        if not company:
            return None
        data["company_id"] = company.id
        data.pop("company_cnpj", None)
        stmt = (
            self.session.query(FinancialStatement)
            .filter(
                FinancialStatement.company_id == company.id,
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
            stmt = FinancialStatement(**{k: v for k, v in data.items() if v is not None})
            self.session.add(stmt)
        return stmt

    def _log_audit(
        self,
        table: str,
        record_id: uuid.UUID,
        operation: str,
        old: dict | None,
        new: dict | None,
    ) -> None:
        audit = AuditLog(
            table_name=table,
            record_id=record_id,
            operation=operation,
            old_values=old,
            new_values=new,
            changed_by=self.job.spider_name,
        )
        self.session.add(audit)
