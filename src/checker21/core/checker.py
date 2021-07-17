
__all__ = ('Checker', 'GitChecker')

import sys
from pathlib import Path

from checker21.management.base import OutputWrapper
from checker21.utils.bash import bash
from checker21.utils.colorize import PALETTES, NO_COLOR_PALETTE


class Checker:

	name = None
	verbose_name = None
	description = None

	def __init__(self, *, stdout=None, stderr=None, style=None):
		self.stdout = stdout or OutputWrapper(sys.stdout)
		self.stderr = stderr or OutputWrapper(sys.stderr)
		self.style = style or PALETTES[NO_COLOR_PALETTE]

	def run(self, subject):
		pass

	def __call__(self, subject):
		self.run(subject)

	def __str__(self):
		return str(self.verbose_name or self.name)

	def __repr__(self):
		return f"<{self.__class__}>[{self}]"

	def clean(self):
		pass


class GitChecker(Checker):
	git_url = None
	target_dir = None

	def __call__(self, subject):
		assert self.git_url, "<GitChecker> should have `git_url` set"
		self.git_clone()
		super().__call__(subject)

	def git_clone(self):
		"""
			Creates a git clone of the repository with checker
			If the repository is cloned already, than it does nothing
		"""
		# check if the repository is cloned
		if self.target_dir:
			path = Path(self.target_dir)
			if path.exists():
				return

		# clone the repository
		cmd_args = ['git', 'clone', self.git_url]
		if self.target_dir:
			cmd_args.append(self.target_dir)
		cmd = bash(cmd_args,
		           stdout = self.stdout,
		           stderr = self.stderr)

	def clean(self):
		"""
			Deletes downloaded git files
		"""
		if self.git_is_ok_to_delete(self.target_dir):
			bash(['rm', '-rf', self.target_dir],
		           stdout = self.stdout,
		           stderr = self.stderr)
		super().clean()

	def git_is_ok_to_delete(self, target_dir):
		"""
			Checks if path is relative
		"""
		if not target_dir:
			return False
		if target_dir == '.':
			return False
		if target_dir.starswith('..'):
			return False
		if target_dir.starswith('/'):
			return False
		return True

