from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class KEXTS_DATA:
    '''
    Dataclass representing a singular Kext item.
    '''
    name: str
    link: str
    version: str
    ver_range: str
