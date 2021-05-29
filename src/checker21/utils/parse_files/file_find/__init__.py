import re
from wcmatch.pathlib import Path
from typing import Generator, List


def parse_pattern(pattern: str) -> List[str]:
    """
    :param pattern: string with rules to find project files;
        * - any characters,
        '\'- escape character,
        ()- groups,
        | - splitting into group elements.
    :return: list of strings with file name rules
    """
    patterns = list()
    # Ищем правило с раширениями файла: начинаются на '.('
    # Далее ищем любые символы исключая точку
    group_extensions = re.findall(r'[.(][^\.]+', pattern)
    if group_extensions:
        # Делаем замену символов точки и скобок на пустую строку,
        # то есть удаляем эти символы
        extensions = re.sub(r'[.()]', '', group_extensions[0])
        # Делаем список с нужными расширениями файлов, разделяя функцией сплит
        extensions_list = extensions.split('|')
        # Ищем правило для имени файла, пасрим все до точки, исключая точку и скобки
        file_name = re.findall(r'[^\.()]+', pattern)
        for extension in extensions_list:
            patterns.append(file_name[0] + '.' + extension)
    else:
        patterns.append(pattern)
    return patterns


def get_files_with_pattern(project_dir: Path, pattern: str = '*', recursive: bool = True) -> Generator:
    """
    :param project_dir: object of class Path, where locate the project
    :param pattern: string with rules to find project files;
        * - any characters,
        '\'- escape character,
        ()- groups,
        | - splitting into group elements.
    :param recursive: search or not in subdirectories
    :return: Iterable object with found files in 'dir'.
    """
    file_patterns = parse_pattern(pattern)
    if not recursive:
        top_level_files = project_dir.glob(file_patterns)
        return top_level_files
    else:
        all_files = project_dir.rglob(file_patterns)
        return all_files
