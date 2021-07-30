from os import PathLike
from typing import Iterable, Generator, Optional, List, Union

from checker21.core import Checker


class Subject:
	bonus: bool

	check_norminette: bool
	program_name: str

	allowed_files: Iterable[str]
	allowed_functions: Iterable[str]

	limit_global_vars: int
	limit_static_vars: int

	checkers: Iterable[Checker]
	_general_checkers: Optional[Iterable[Checker]]
	_all_files: Optional[List[Union[str, PathLike]]]

	def __init__(self) -> None: ...

	def get_checkers(self) -> Generator[Checker, None, None]: ...
	def list_files(self) -> List[Union[str, PathLike]]: ...
