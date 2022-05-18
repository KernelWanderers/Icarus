import requests
from src.util.utils import get_root_dir
from src.util.constants import PERCENT, OK, FAILED
from src.data_types.acpi_data import ACPI_DATA

root = get_root_dir()


class ACPIListObtainer:
    '''
    Instance responsible for obtaining a comprehensive list of available ACPI files.
    Both pre-compiled and DSL (decompiled).

    Credit: [Dortania](https://github.com/dortania) \n
    Source: https://github.com/dortania/Getting-Started-With-ACPI/tree/master/extra-files
    '''

    def __init__(self):
        self.acpi = {
            'compiled': [],
            'decompiled': []
        }
        self.url = 'https://github.com/dortania/Getting-Started-With-ACPI/raw/master/extra-files'

        try:
            print(f'{PERCENT} Running ACPI integrity validation...')

            if self.test():
                raise RuntimeError(
                    f'{FAILED}' +
                    'Something went wrong when validating the integrity of "ACPI" data type.\n' +
                    'This should not happen — please report this at our issues page.'
                )

            print(f'{OK} ACPI integrity validity check completed successfully.')
        except RuntimeError as err:
            print(str(err))
        try:
            print(f'{PERCENT} Attempting to fetch precompiled ACPI patches...')
            self.get_files('/compiled')
            print(f'{OK} Successfully fetched precompiled ACPI patches.')
        except Exception as err:
            print(f'{FAILED} Failed to fetch precompiled ACPI patches.')
            print(f'\t^^^^^^{str(err)}')

        try:
            print(f'{PERCENT} Attempting to fetch empty ACPI patches...')
            self.get_files('/decompiled')
            print(f'{OK} Successfully fetched empty ACPI patches.')
        except Exception as err:
            print(f'{FAILED} Failed to fetch empty ACPI patches.')
            print(f'\t^^^^^^{str(err)}')

    def get_files(self, endpoint: str = '') -> None:
        '''
        Obtains ACPI files from Dortania's 'Getting Started With ACPI' repository.
        '''

        if not endpoint:
            return

        collecting = False

        data = requests.get(self.url + endpoint).text

        for line in data.split('\n'):
            if 'box mb-3' in line.lower():
                collecting = True
                continue

            if collecting:
                if 'class="footer' in line.lower():
                    collecting = False
                    break

                if 'dsl' in line.lower() or 'aml' in line.lower():
                    if '.zip' in line.lower():
                        continue

                    if '<a' in line.lower() and \
                        'ssdt' in line.lower() and \
                            not 'commit' in line.lower():
                        name = line.split('title="')
                        link = line.split('href="')

                        if len(name) > 1:
                            name = name[1].split('"')[0]

                        if len(link) > 1:
                            link = 'https://github.com' + \
                                link[1].split('"')[0].replace('blob', 'raw')

                        file_type = name.split('.')

                        if len(file_type) > 1:
                            file_type = file_type[1]
                        else:
                            file_type = 'unknown'

                        self.acpi.get(
                            'decompiled' if '/decompiled' == endpoint else 'compiled', []
                        ).append(ACPI_DATA(name, file_type, link))

    def validate_acpi_list(self, acpis: list) -> list:
        failed = []

        for acpi in acpis:
            if not isinstance(acpi, ACPI_DATA):
                failed.append(acpi)

        return failed

    def test(self) -> bool:
        test_acpi = [
            ACPI_DATA(name='SSDT-AWAC.aml',
                      link='https://google.com', file_type='aml'),
            {'foo': 'bar'}
        ]

        return not self.validate_acpi_list(test_acpi)
