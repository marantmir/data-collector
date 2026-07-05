from sources.base import DataSourceConnector
from sources.brasilapi import BrasilAPIConnector
from sources.cnpja import CNPJaConnector


def get_connector(name: str = "brasilapi", **kwargs) -> DataSourceConnector:
    connectors = {
        "brasilapi": BrasilAPIConnector,
        "cnpja": CNPJaConnector,
    }
    cls = connectors.get(name)
    if not cls:
        raise ValueError(f"Unknown connector: {name}. Options: {list(connectors.keys())}")
    return cls(**kwargs)
