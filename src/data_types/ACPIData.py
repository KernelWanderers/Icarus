from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class ACPIData:
    name: str
    file_type: str
    link: str