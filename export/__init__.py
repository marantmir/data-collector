from export.csv_exporter import CSVExporter
from export.sped_exporter import SPEDExporter
from export.xml_exporter import XMLExporter


def get_exporter(fmt: str):
    exporters = {
        "csv": CSVExporter,
        "xml": XMLExporter,
        "sped": SPEDExporter,
    }
    cls = exporters.get(fmt)
    if not cls:
        raise ValueError(f"Unknown format: {fmt}. Options: {list(exporters.keys())}")
    return cls()
