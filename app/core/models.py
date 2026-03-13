from dataclasses import dataclass


@dataclass
class DimState:
    name: str
    value: float = 5.0