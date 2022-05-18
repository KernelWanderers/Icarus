from dataclasses import dataclass


@dataclass(frozen=True, eq=True)
class ACPI_DATA:
    '''
    Dataclass representing a singular ACPI item.
    '''
    name: str
    file_type: str
    link: str
