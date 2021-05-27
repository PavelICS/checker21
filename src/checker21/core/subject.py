from checker21.checkers import *
from checker21.application import app


__all__ = ('Subject',)


class SubjectBase(type):

	def __new__(mcs, name, bases, attrs, **kwargs):
		new_cls = super().__new__(mcs, name, bases, attrs, **kwargs)  # type: Subject
		# Also ensure initialization is only performed for subclasses of Model
		# (excluding Model class itself).
		parents = [b for b in bases if isinstance(b, SubjectBase)]
		if not parents:
			return new_cls

		app.register_project(new_cls)
		return new_cls


class Subject(metaclass=SubjectBase):
	bonus = False

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

