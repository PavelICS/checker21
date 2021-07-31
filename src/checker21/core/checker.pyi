from typing import Union, Optional
from typing.io import IO

from checker21.core import Subject, Project
from checker21.utils.colorize.palette import Palette


class Checker:
	name: str
	verbose_name: str
	description: str

	stdout: Union[None, int, IO]
	stderr: Union[None, int, IO]
	style: Optional[Palette]

	def __init__(self) -> None: ...

	def init_io(
			self,
			stdout: Union[None, int, IO] = ...,
			stderr: Union[None, int, IO] = ...,
			style: Optional[Palette] = ...
	) -> None: ...

	def run(self, project: Project, subject: Subject) -> None: ...

	def __call__(self, project: Project, subject: Subject) -> None: ...

	def __str__(self) -> str: ...

	def __repr__(self) -> str: ...

	def clean(self, project: Project) -> None: ...


class GitChecker(Checker):
	git_url: str
	target_dir: str

	def git_clone(self) -> None: ...

	def git_is_ok_to_delete(self, target_dir: str) -> bool: ...
