import os
import sys
import platform

from src.data_types.kexts_data import KEXTS_DATA
from .text import COLORS, FORMAT

end_fmt = FORMAT['end_formatting']
dir_delim = '\\' if platform.system().lower() == 'windows' else '/'


def color_text(text, color) -> str:
    return f'{COLORS.get(color, "green")}{text}{end_fmt}'


def format_text(text, formats) -> str:
    formats = formats.split('+')
    final_string = text

    for fmt in formats:
        selected = FORMAT.get(fmt)

        if not selected:
            continue

        final_string = f'{selected}{final_string}{end_fmt}'

    return final_string


def title(name, additional=0) -> None:
    spaces = ' ' * int((53 - len(name)) / 2)
    additional = ' ' * additional

    print(color_text(' ' * 2 + '#' * 55, 'cyan'))
    print(color_text(' #' + spaces + name + spaces + additional + '#', 'cyan'))
    print(color_text('#' * 55 + '\n' * 2, 'cyan'))


def clear() -> None:
    if sys.platform == 'win32':
        os.system('cls')
    elif sys.platform == 'darwin':
        # Special thanks to [A.J Uppal](https://stackoverflow.com/users/3113477/a-j-uppal) for this!
        # Original comment: https://stackoverflow.com/a/29887659/13120761

        # But, with more cursed bullshit!
        print('\033c', end='')
        print('\033[3J', end='')
        print('\033c', end='')
    elif sys.platform == 'linux':
        os.system('clear')


def get_root_dir() -> str:
    root_dir = ''

    if getattr(sys, 'frozen', False):
        root_dir = os.path.dirname(sys.executable)
        os.chdir(root_dir)
    else:
        root_dir = os.path.dirname(os.path.abspath(__file__))

    if 'src' in root_dir.lower().split(dir_delim):
        root_dir = dir_delim.join(root_dir.split(dir_delim)[:-1])

    return root_dir


def file_diff(a, b) -> list:
    diff = []

    if not a or not b:
        return a or b

    for i in range(len(a)):
        matches = False

        for j in range(len(b)):
            cond = a[i][1].version == b[j][1].version \
                if type(a[i][1]) == KEXTS_DATA and type(b[j][1]) == KEXTS_DATA \
                else a[i][1].name == b[j][1].name

            if cond:
                matches = True
                break

        if not matches:
            diff.append(a[i])

    return diff
