from os import PathLike
from types import ModuleType
from typing import Union, List, Dict, Optional

from checker21.core import Subject
from checker21.utils.files import CurrentPath


class Project:
	name: str
	verbose_name: str
	description: str

	path: CurrentPath
	temp_folder: CurrentPath

	_module: Optional[ProjectModule]
	_all_files: Optional[List[Union[str, PathLike]]]

	def __init__(self, path: CurrentPath, temp_folder: CurrentPath) -> None: ...

	def get_subjects(self) -> List[Subject]: ...
	def list_files(self) -> List[Union[str, PathLike]]: ...


def find_projects(target_dir: Union[List[PathLike], PathLike, str]) -> List[str]: ...
def get_projects() -> Dict[str, ProjectModule]: ...


class ProjectModule:
	name: str
	pkg_name: str
	pkg: ModuleType
	_module: Optional[ModuleType]

	def __init__(self, name: str, pkg_name: str, pkg: ModuleType) -> None: ...

	def load(self) -> ModuleType: ...

	def __str__(self) -> str: ...

	def __repr__(self) -> str: ...
