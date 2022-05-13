import requests
from sys import exit
from src.data_types.KextsData import KextsData
from src.util.Utils import color_text


class KextsListObtainer:
    '''
    Instance responsible for obtaining a comprehensive list of available Kexts.

    Credit: [Dortania](https://github.com/dortania) \n
    Source: https://github.com/dortania/build-repo/blob/builds/config.json
    '''

    def __init__(self):
        self.kexts: list[KextsData] = []
        self.url = 'https://raw.githubusercontent.com/dortania/build-repo/builds/config.json'

        try:
            print(f'[    {color_text("%" , "cyan")}    ]: Running integrity verification...')

            if not self.test():
                raise RuntimeError(f'[  {color_text("FAILED", "red")}  ]: Something went wrong when verifying integrity of data types. '
                                   'This should not happen — please report this at our issues page.'
                                   )
            else:
                print(
                    f'[    {color_text("OK", "green")}    ]: Integrity verification check completed successfully.')
        except Exception as e:
            print(f'{str(e)}')

        self.fetch_list()

    def fetch_list(self):
        try:
            print(f'[    {color_text("%" , "cyan")}    ]: Fetching Kexts list...')
            r = requests.get(self.url).json()
            filtered = {}

            for key in r.keys():
                if r.get(key) and \
                    type(r[key]) == dict and \
                        r[key].get('type', 'unknown').lower() == 'kext':

                    filtered[key] = r[key]
        except Exception as e:
            print(f'[  {color_text("FAILED", "red")}  ]: Something went wrong during the fetching process. This should not happen — please report this at our issues page.')
            print(f'\t^^^^^^{str(e)}')
            exit(0)

        print(f'[    {color_text("OK", "green")}    ]: Successfully obtained Kexts list.')

        for key in filtered.keys():
            n = 0
            filtered_ver = {
                key: {
                    'versions': []
                }
            }

            while True:
                versions = filtered[key]['versions']

                if n >= len(versions):
                    break

                if not any(versions[n].get('version', '') == d.get('version', '') for d in filtered_ver[key].get('versions', [])):
                    filtered_ver[key]['versions'].append(
                        versions[n]
                    )

                n += 1

            for key in filtered_ver.keys():
                versions = filtered_ver[key].get('versions', [])

                alt = [tuple(x.get('version', '0.0.0').rsplit('.'))
                       for x in versions]
                high = '.'.join(max(alt))
                low = '.'.join(min(alt))

                print(
                    f'[    {color_text("%" , "cyan")}    ]: Attempting to map {key} (v{low} - v{high})...')

                try:
                    for version in versions:
                        ver = version.get('version', '')
                        self.kexts.append(
                            KextsData(
                                name=key,
                                link=version.get('links', {}).get('release', ''),
                                version=ver,
                                ver_range=f'v{low}-v{high}'
                            )
                        )

                    print(
                        f'[    {color_text("OK", "green")}    ]: Successfully mapped {key} (v{low} - v{high})!')
                except Exception as e:
                    print(
                        f'[  {color_text("FAILED", "red")}  ]: Failed to map {key} (v{low} - v{high})! This shouldn\'t happen — please report this at our issue page.')
                    print(f'\t^^^^^^{str(e)}')

    def validate_item(self, item) -> bool:
        if type(item) == dict:
            for key in item.keys():
                if key.lower() != 'name' and \
                        key.lower() != 'link_rel' and \
                        key.lower() != 'link_debug' and \
                        key.lower() != 'version' and \
                        key.lower() != 'ver_range':
                    return False
        else:
            return isinstance(item, KextsData)

        return True

    def validate_kexts_list(self, kexts=[]) -> list:
        failed = []

        for kext in kexts:
            if not self.validate_item(kext):
                failed.append(kext)

        return failed
        # return

    def test(self) -> bool:
        test_kexts = [
            KextsData(name='Lilu.kext', link='https://google.com', version='2.1.5', ver_range='v2.0.8-v2.1.5'),

            {'name': 'WhateverGreen.kext', 'link': 'https://google.com', 'version': '2.1.5'},

            # Should fail here upon validation – otherwise, something's definitely wrong.
            {'lff': 123}
        ]

        if self.validate_kexts_list(test_kexts):
            return True

        return False
