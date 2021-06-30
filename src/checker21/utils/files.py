import re
from pathlib import Path

def compile_path_pattern(pattern):
	# escape symbol '.' if slash count is even
	pattern = re.sub(r'(?<!\\)((?:\\\\)*)\.', r'\1\.', pattern)
	# replace '*' to '.*' if slash count is even
	pattern = re.sub(r'(?<!\\)((?:\\\\)*)\*', r'\1.*', pattern)
	# replace '?' to '.' if slash count is even and > 0
	pattern = re.sub(r'(?<!\\)((?:\\\\)+)\?', r'\1.', pattern)
	# replace '?' to '.' if there is no symbol before ")]\"
	pattern = re.sub(r'(?<![\\\]\)])\?', r'.', pattern)
	return re.compile(f"^{pattern}$")


def find_files(path, *, recursive=True):
	path = Path(path)
	for file in path.iterdir():
		if recursive and file.is_dir():
			yield from find_files(file, recursive=recursive)
		if file.is_file():
			yield file

def find_files_by_pattern(path, pattern, *, recursive=True):
	regexp = compile_path_pattern(pattern)
	for file in find_files(path, recursive=recursive):
		if regexp.match(str(file)):
			yield file

