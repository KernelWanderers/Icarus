from src.core.KextsList import KextsListObtainer
from src.core.ACPIList import ACPIListObtainer
from src.cli.UI import UI

KLO = KextsListObtainer()
ACPI = ACPIListObtainer()

UI = UI(kexts=KLO.kexts, acpi=ACPI.acpi)

UI.create_ui()