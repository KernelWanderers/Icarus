import os
import sys
import zipfile
import shutil
from urllib.request import urlretrieve
from src.data_types.KextsData import KextsData
from src.data_types.ACPIData import ACPIData
from src.util.Utils import dir_delim, color_text, format_text, title, clear, get_root_dir, file_diff


class UI:
    def __init__(self, kexts=[], acpi=[]):
        self.acpi = acpi
        self.efi = ''
        self.latest_expanded = None
        self.kexts = kexts
        self.state = ''
        self.to_download = []
        self.toggled = {
            'selected': [],
            'deselected': [],
        }

    def handle_command(self, opts=[]):
        cmd = input('\n\nPlease select an option: ')
        valid = False

        for opt in opts:
            if cmd.upper() == opt[0].upper() or \
                    cmd.upper() == opt[1].upper():
                clear()
                self.title()
                data = opt[2]()

                print(data if data else 'Successfully executed.\n')
                self.enter()

                clear()
                self.create_ui()
                valid = True

        if not valid:
            clear()
            print('Invalid option!\n')
            self.enter()

            clear()
            self.create_ui()

    def available_kexts(self):
        clear()
        self.title()

        kexts = self.kexts
        listed = []
        diff = 0
        amount = 0
        associated = {}

        for i in range(len(kexts)):
            if kexts[i].name in listed:
                diff += 1
                continue

            fmt_text = format_text(kexts[i].name, 'underline')

            print(
                f'({i - diff + 1}) - {fmt_text} {kexts[i].ver_range}'
            )
            if i == 0:
                associated[kexts[i].name] = kexts[i]
            else:
                low, high = self.get_range_kext(kexts[i].name, kexts)
                associated[kexts[i].name] = kexts[low:high]

            amount += 1
            listed.append(kexts[i].name)

        option = input(
            f'\n\nPlease select an option (1-{amount}, \'Q\' to quit, or \'R\' to return): ')

        if 'r' in option.lower():
            self.return_state()
        elif 'q' in option.lower():
            self.quit()

        try:
            num = int(option)
        except Exception:
            print(color_text('Invalid option!', 'red') + '\n')
            self.enter()

            return self.available_kexts()

        if num < 1 or num > amount:
            print(color_text(
                f'Out of range! Possible range: 1-{amount}', 'red') + '\n')
            self.enter()

            return self.available_kexts()

        self.state = 'kexts'

        associated_keys = associated.keys()

        for n in range(len(associated_keys)):
            if num - 1 == n:
                self.latest_expanded = associated[list(associated_keys)[n]]

                self.state = 'expanded_kexts'

                self.expand_item(self.latest_expanded)
                break

    def available_acpi_pre(self):
        precompiled = self.acpi.get('compiled', [])

        self.state = 'expanded_acpi_pre'

        self.expand_item(precompiled)

    def available_acpi_dsl(self):
        empty = self.acpi.get('decompiled', [])

        self.state = 'expanded_acpi_dsl'

        self.expand_item(empty)

    def nav_efi(self):
        clear()
        self.title()

        path = input('\n\nPlease supply a path to your EFI: ')

        if not path:
            clear()
            self.title()

            print(color_text('\n\nYou must supply a path!', 'red'))
            self.enter()

            return self.nav_efi()

        if '~' in path.lower():
            path = path.replace('~', os.path.expanduser('~'))

        if not os.path.isdir(path):
            clear()
            self.title()

            print(color_text('\n\nInvalid path!', 'red'))
            self.enter()

            return self.nav_efi()

        self.efi = os.path.join(path.replace('/', dir_delim), '')

        if os.path.isdir(os.path.join(self.efi, 'OC')):
            self.efi = os.path.join(self.efi, 'OC')

    def downloads_list(self):
        if not self.to_download:
            print('\n\nNo files assigned to download yet!')
            self.enter()

            return self.create_ui()

        self.state = 'down_list'

        print(self.to_download)

        return self.expand_item(self.to_download, removal=True)

    def download_files(self):
        clear()
        self.title()

        if not self.to_download:
            print(color_text(
                '\n\nNo items to download! Please select some and try again.', 'red'))
            self.enter()

            return self.create_ui()

        path = self.efi

        if not path:
            _ACPI = os.path.join(path, 'ACPI')
            _KEXTS = os.path.join(path, 'Kexts')

            if not os.path.isdir(_ACPI):
                os.mkdir(_ACPI)

            if not os.path.isdir(_KEXTS):
                os.mkdir(_KEXTS)

            path = get_root_dir()

            if 'src' in path.lower():
                path = dir_delim.join(path.split(dir_delim)[:-1])

        zips = []

        for item in self.to_download:
            sub = 'Kexts' if type(item[1]) == KextsData else 'ACPI'

            u_name = format_text(item[1].name, 'underline')

            try:
                print(
                    f'\n\n[    {color_text("%" , "cyan")}    ]: Trying to download "{u_name}"...')

                dump_path = os.path.join(path, sub)

                urlretrieve(
                    item[1].link,
                    os.path.join(dump_path, item[1].link.split('/')[-1])
                )

                if sub == 'Kexts':
                    if '.zip' in item[1].link.split('/')[-1]:
                        zips.append((item[1].name, os.path.join(
                            dump_path, item[1].link.split('/')[-1])))

                print(
                    f'[    {color_text("OK", "green")}    ]: Successfully downloaded "{u_name}" into "{format_text(dump_path, "underline")}"!')
            except Exception as e:
                print(
                    f'[  {color_text("FAILED", "red")}  ]: Failed to download "{u_name}"!')
                print(f'\t^^^^^^{str(e)}')

        # Files to not remove.
        no_rem = []
        zip_dir = ''

        for _zip in zips:
            u_name, zip = _zip
            zip_name = zip.split(dir_delim)[-1]
            kext = u_name.split('.')[0].split('-')[0] + '.kext'
            no_rem.append(kext)

            if not zip_dir:
                zip_dir = dir_delim.join(zip.split(dir_delim)[:-1])

            with zipfile.ZipFile(zip, 'r') as ref:

                try:
                    print(
                        f'\n\n[    {color_text("%" , "cyan")}    ]: Extracting "{zip_name}"...')

                    ref.extractall(zip_dir)
                    print(
                        f'[    {color_text("OK", "green")}    ]: Successfully extracted "{zip_name}"!')
                    ref.close()

                    if "virtual" in kext.lower():
                        shutil.move(
                            os.path.join(zip_dir, 'Kexts', kext),
                            os.path.join(zip_dir, kext)
                        )

                    os.remove(zip)
                    print(
                        f'[    {color_text("OK", "green")}    ]: Removed ZIP file!')

                except Exception as e:
                    print(
                        f'[  {color_text("FAILED", "red")}  ]: Failed to extract "{zip_name}"!')
                    print(f'\t^^^^^^{str(e)}')
                    ref.close()

                    continue

        if zip_dir:
            items = os.listdir(zip_dir)
            success = False

            for i in items:
                # Item path
                ip = os.path.join(zip_dir, i)

                if i in no_rem:
                    continue

                if 'Tools' == i:
                    shutil.rmtree(ip)
                    continue

                if '.dsym' in i.lower() or \
                        zip_name.split('.')[0].lower() + '.kext' != i.lower():
                    if os.path.isfile(ip):
                        os.remove(ip)
                    else:
                        shutil.rmtree(ip)

                    success = True

            if success:
                print(
                    f'[    {color_text("OK", "green")}    ]: Removed redundant files!')

        self.to_download = []

    def create_ui(self):
        commands = [
            (color_text('K. ', 'yellow'), 'Available Kexts'),
            (color_text('P. ', 'yellow'), 'Available ACPI prebuilt patches'),
            (color_text('M. ', 'yellow'), 'Available ACPI DSL files (manual method)'),
            (color_text('E. ', 'yellow'), 'Navigate to EFI'),
            (color_text('D. ', 'yellow'), 'Downloads list'),
            (color_text('C. ', 'yellow'), 'Complete and download files'),
            ('\n\n' + color_text('Q. ', 'yellow'), 'Quit')
        ]

        cmd_opts = [
            ('K', 'K.', self.available_kexts),
            ('P', 'P.', self.available_acpi_pre),
            ('M', 'M.', self.available_acpi_dsl),
            ('E', 'E.', self.nav_efi),
            ('D', 'D.', self.downloads_list),
            ('C', 'C.', self.download_files),
            ('Q', 'Q.', self.quit)
        ]

        try:
            clear()
            self.title()

            for cmd in commands:
                print(''.join(cmd))

            self.handle_command(cmd_opts)
        except Exception as e:
            raise e

    def get_range_kext(self, name: str, kexts=[]) -> tuple[int, int]:
        if not kexts:
            return (-1, -1)

        i = 0
        low = -1
        high = -1

        while True:
            if i >= len(kexts):
                high = i
                break

            if kexts[i].name.lower() == name.lower():
                if low == -1:
                    low = i

            elif low > 0:
                high = i - 1
                break

            i += 1

        return (low, high)

    def handle_opt(self, option='', item=None, states=[], removal=False):
        if not option:
            return

        if 'r' in option.lower():
            if self.state != 'down_list':

                if self.toggled.get('selected', []) or self.toggled.get('deselected', []):
                    confirm = input(format_text(
                        'You have unsaved changes! Save now? (Y/N): ', 'underline+bold'))

                    if 'y' in confirm.lower():
                        self.confirm_expand()

            self.return_state()
        elif 'q' in option.lower():
            self.quit()
        elif 'c' in option.lower():
            self.confirm_expand()

            return self.expand_item(item, states, removal)

        try:
            num = int(option)
        except Exception:
            print(color_text('Invalid option(s)!', 'red') + '\n')
            self.enter()

            return self.expand_item(item, states, removal)

        if num < 1 or num > len(states):
            print(color_text(
                f'Out of range! Possible range: 1-{len(states)}', 'red') + '\n')
            self.enter()

            return self.expand_item(item, states, removal)

        _data = (not states[num - 1][0], states[num - 1][1])

        self.toggled.get(
            'selected' if _data[0] else 'deselected', []).append(_data)

        states[num - 1] = _data

        return states

    def confirm_expand(self):
        add = 0
        rem = 0

        sel = self.toggled.get('selected', [])
        desel = self.toggled.get('deselected', [])

        if sel:
            self.to_download = self.to_download + sel
            add = len(sel)
            self.toggled['selected'] = []

        if desel:
            self.to_download = file_diff(self.to_download, desel)
            rem = len(desel)
            self.toggled['deselected'] = []

        first_msg = ''
        snd_msg = ''

        if add > 0:
            first_msg = color_text(
                f'\nSuccessfully added {add} item(s) to download list!',
                'green'
            )

        if rem > 0:
            snd_msg = color_text(
                f'\nSuccessfully removed {rem} item(s) from download list!',
                'green'
            )

        print(
            '\n' +
            first_msg +
            snd_msg
        )
        self.enter()

    def expand_item(self, item, _states=[], removal=False):
        if not item and len(_states) < 1:
            return self.available_kexts()

        clear()
        self.title()

        if not item and len(_states):
            states = _states

        elif type(item) == list:
            states = [(any(x[1].version == data.version if hasattr(x[1], 'version') and hasattr(data, 'version') else x[1].name == data.name for x in self.to_download), data) if type(
                data) != tuple else data for data in item]

        else:
            states = [
                (any(x[1].version == item.version if hasattr(x[1], 'version') and hasattr(item, 'version') else x[1].name == item.name for x in self.to_download), item)]

        for i in range(len(states)):
            try:
                ver = ''

                if type(states[i][1]) == KextsData:
                    ver = f'(v{states[i][1].version})'

                txt = f'({i + 1}) — ' + \
                    ('[X] ' if states[i][0] else '[ ] ') + \
                    f'{states[i][1].name} {ver}'
                coloured = color_text(txt, 'green') if states[i][0] else txt

                print(coloured)
            except Exception as e:
                raise e

        print(format_text(
            '\n\nNOTE: Options can also be separated with a `,` to supply multiple options simultaneously', 'underline+bold'))
        option = input(
            f'Please select an option (1-{len(states)}, \'Q\' to quit, \'C\' to confirm, or \'R\' to return): ')

        if ',' in option:
            opts = option.split(',')
            states_data = []

            for opt in opts:
                states_data = self.handle_opt(opt, item, states, removal)

            states = states_data
        else:
            states_data = self.handle_opt(option, item, states, removal)

        return self.expand_item(None, states, removal)

    def return_state(self):
        match self.state:
            case 'kexts' | 'expanded_acpi_pre' | 'expanded_acpi_dsl' | 'down_list':
                return self.create_ui()
            case 'expanded_kexts':
                self.state = 'kexts'
                return self.available_kexts()

    def quit(self):
        clear()
        sys.exit(0)

    def title(self):
        title('Icarus', 1)

    def enter(self):
        # “Hacky” way of detecting when
        # the Enter key is pressed down.
        #
        # Source: https://github.com/KernelWanderers/OCSysInfo/blob/main/src/cli/ui.py
        if input(color_text('Press [enter] to return... ', 'yellow')) is not None:
            return
