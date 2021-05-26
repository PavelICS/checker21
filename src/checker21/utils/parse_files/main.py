from wcmatch.pathlib import Path

from file_find import get_files_with_pattern


if __name__ == '__main__':
    project_dir = Path('/Users/talpa/Dev/Dev/test_open_file/')
    pattern = '*.(c|out|py)'
    recursive = True
    files = get_files_with_pattern(project_dir, pattern, recursive)
    for item in files:
        print(item, '------', item.name)
