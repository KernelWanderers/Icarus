from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class KextsData:
    name: str
    link: str
    version: str
    ver_range: str