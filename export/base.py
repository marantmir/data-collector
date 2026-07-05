from abc import ABC, abstractmethod

from db.models.company import Company


class BaseExporter(ABC):
    format: str = "base"

    @abstractmethod
    def export_companies(self, companies: list[Company], **kwargs) -> str:
        ...

    @abstractmethod
    def export_company(self, company: Company, **kwargs) -> str:
        ...

    def _format_cnpj(self, cnpj: str) -> str:
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
