import os
import re
from os import PathLike
from pathlib import Path, WindowsPath, PosixPath
from typing import Pattern, Union, Generator, Callable


def compile_path_pattern(pattern: str) -> Pattern:
	# escape symbol '.' if slash count is even
	pattern = re.sub(r'(?<!\\)((?:\\\\)*)\.', r'\1\.', pattern)
	# replace '*' to '.*' if slash count is even
	pattern = re.sub(r'(?<!\\)((?:\\\\)*)\*', r'\1.*', pattern)
	# replace '?' to '.' if slash count is even and > 0
	pattern = re.sub(r'(?<!\\)((?:\\\\)+)\?', r'\1.', pattern)
	# replace '?' to '.' if there is no symbol before ")]\"
	pattern = re.sub(r'(?<![\\\]\)])\?', r'.', pattern)
	return re.compile(f"^{pattern}$")


def find_files(path: Union[str, PathLike], *, recursive: bool = True) -> Generator[Path, None, None]:
	path = Path(path)
	for file in path.iterdir():
		if recursive and file.is_dir():
			yield from find_files(file, recursive=recursive)
		if file.is_file():
			yield file


def find_files_by_pattern(
		path: Union[str, PathLike],
		pattern: str,
		*,
		recursive: bool = True
) -> Generator[Path, None, None]:

	regexp = compile_path_pattern(pattern)
	for file in find_files(path, recursive=recursive):
		if regexp.match(str(file)):
			yield file


def update_file_with_backup(path: Union[str, PathLike], callback: Callable[[bytes], bytes]):
	file = Path(path)
	backup = file.with_suffix(file.suffix + '.backup')
	if backup.exists():
		return
	with file.open('rb') as f:
		data = f.read()
	with backup.open('wb') as f:
		f.write(data)
	with file.open('wb') as f:
		f.write(callback(data))


active_path = os.getcwd()
active_path_list = []


class CurrentPath(Path):
	def __new__(cls, *args, **kwargs):
		if cls is CurrentPath:
			cls = CurrentWindowsPath if os.name == 'nt' else CurrentPosixPath
		self = cls._from_parts(args, init=False)
		if not self._flavour.is_supported:
			raise NotImplementedError("cannot instantiate %r on your system" % (cls.__name__,))
		self._init()
		return self

	def __enter__(self):
		global active_path
		active_path_list.append(active_path)
		os.chdir(self)
		active_path = self
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		global active_path
		active_path = active_path_list.pop()
		os.chdir(active_path)


class CurrentWindowsPath(CurrentPath, WindowsPath):
	pass


class CurrentPosixPath(CurrentPath, PosixPath):
	pass
