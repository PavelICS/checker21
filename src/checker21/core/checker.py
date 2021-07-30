__all__ = ('Checker', 'GitChecker')

import sys
from pathlib import Path

from checker21.utils.bash import bash
from checker21.utils.colorize import PALETTES, NO_COLOR_PALETTE


class Checker:
	name = ''
	verbose_name = ''
	description = ''

	def __init__(self):
		self.stdout = None
		self.stderr = None
		self.style = None

	def init_io(self, stdout=None, stderr=None, style=None):
		from checker21.management.base import OutputWrapper
		self.stdout = stdout or OutputWrapper(sys.stdout)
		self.stderr = stderr or OutputWrapper(sys.stderr)
		self.style = style or PALETTES[NO_COLOR_PALETTE]

	def run(self, project, subject):
		pass

	def __call__(self, project, subject):
		self.run(project, subject)

	def __str__(self):
		return str(self.verbose_name or self.name)

	def __repr__(self):
		return f"<{self.__class__}>[{self}]"

	def clean(self, project):
		pass


class GitChecker(Checker):
	git_url = ''
	target_dir = ''

	def __call__(self, project, subject):
		assert self.git_url, "<GitChecker> should have `git_url` set"
		with project.temp_folder:
			self.git_clone()
			super().__call__(project, subject)

	def git_clone(self):
		"""
			Creates a git clone of the repository with checker
			If the repository is cloned already, than it does nothing
		"""
		target_dir = self.target_dir
		# check if the repository is cloned
		if target_dir:
			path = Path(target_dir)
			if path.exists():
				return

		# clone the repository
		cmd_args = ['git', 'clone', self.git_url]
		if target_dir:
			cmd_args.append(target_dir)
		cmd = bash(cmd_args,
					stdout=self.stdout,
					stderr=self.stderr)

	def clean(self, project):
		"""
			Deletes downloaded git files
		"""
		with project.temp_folder:
			if self.git_is_ok_to_delete(self.target_dir):
				bash(['rm', '-rf', self.target_dir],
					stdout=self.stdout,
					stderr=self.stderr)
		super().clean(project)

	def git_is_ok_to_delete(self, target_dir):
		"""
			Checks if path is relative
		"""
		if not target_dir:
			return False
		if target_dir == '.':
			return False
		if target_dir.startswith('..'):
			return False
		if target_dir.startswith('/'):
			return False
		return True
