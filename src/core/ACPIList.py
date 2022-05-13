import os
import sys
import requests
from src.util.Utils import get_root_dir, color_text
from src.data_types.ACPIData import ACPIData

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
            print(f'[    {color_text("%" , "cyan")}    ]: Attempting to fetch precompiled ACPI patches...')
            self.get_files('/compiled')
            print(f'[    {color_text("OK", "green")}    ]: Successfully fetched precompiled ACPI patches.')
        except Exception as e:
            raise e
            print(f'[  {color_text("FAILED", "red")}  ]: Failed to fetch precompiled ACPI patches.')
            print(f'\t^^^^^^{str(e)}')

        try:
            print(f'[    {color_text("%" , "cyan")}    ]: Attempting to fetch empty ACPI patches...')
            self.get_files('/decompiled')
            print(f'[    {color_text("OK", "green")}    ]: Successfully fetched empty ACPI patches.')
        except Exception as e:
            print(f'[  {color_text("FAILED", "red")}  ]: Failed to fetch empty ACPI patches.')
            print(f'\t^^^^^^{str(e)}')

    def get_files(self, endpoint):
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
                    
                    if '<a' in line.lower() and 'ssdt' in line.lower() and not 'commit' in line.lower():
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
                        ).append(ACPIData(name, file_type, link))
