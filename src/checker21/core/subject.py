__all__ = ('Subject',)

from checker21.checkers import *


class Subject:
	bonus = False
	check_norminette = False
	program_name = ''

	allowed_files = []
	allowed_functions = []

	limit_global_vars = -1
	limit_static_vars = -1

	actions = []
	checkers = []

	_general_checkers = None
	_source_files = None

	def __init__(self):
		checkers = []
		if self.allowed_files:
			checkers.append(ForbiddenFilesChecker())
		if self.check_norminette:
			checkers.append(NorminetteChecker())
		self._general_checkers = checkers

	def get_checkers(self):
		if self._general_checkers:
			yield from self._general_checkers
		if self.checkers:
			yield from self.checkers

	def get_source_files(self):
		if self._source_files is not None:
			return self._source_files

		# self._source_files = TODO find source files
		return self._source_files
