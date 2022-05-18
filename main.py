from src.core.kexts_list import KextsListObtainer
from src.core.acpi_list import ACPIListObtainer
from src.cli.ui import UI

KLO = KextsListObtainer()
ACPI = ACPIListObtainer()

UI = UI(kexts=KLO.kexts, acpi=ACPI.acpi)

UI.create_ui()