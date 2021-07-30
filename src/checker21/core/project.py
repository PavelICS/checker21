import functools
import pkgutil
from pathlib import Path
from importlib import import_module

from checker21.conf import settings


class Project:
	name = ''
	verbose_name = ''
	description = ''

	_module = None

	def __init__(self, path, temp_folder):
		self.path = path
		self.temp_folder = temp_folder

	def get_subjects(self):
		from checker21.application import app
		return app.get_subjects(self._module.name)


def find_projects(target_dir):
	"""
	Given a path to a projects directory, return a list of all project names that are available.
	"""
	target_dir = target_dir if isinstance(target_dir, list) else [Path(target_dir)]
	return [
		name
		for _, name, is_pkg in pkgutil.iter_modules(target_dir)
		if is_pkg and not name.startswith('_')
	]


@functools.lru_cache(maxsize=None)
def get_projects():
	"""
	Return a dictionary mapping project names to their callback module.
	The dictionary is in the format {project_name: Project}.
	The dictionary is cached on the first call and reused on subsequent
	calls.
	"""
	projects = {}
	if settings.INTERNAL_PROJECTS_REPOSITORY:
		module = import_module(str(settings.INTERNAL_PROJECTS_REPOSITORY))
		module_name = module.__name__.split('.')[0]
		projects = {
			name: ProjectModule(name, module_name, module)
			for name in find_projects(module.__path__)
		}

	if settings.EXTRA_PROJECTS_MODULE:
		extra_module = import_module(str(settings.EXTRA_PROJECTS_MODULE))
		projects.update({
			name: ProjectModule(name, extra_module.__name__, extra_module)
			for name in find_projects(extra_module.__path__)
		})

	return projects


class ProjectModule:
	__slots__ = 'name', 'pkg_name', 'pkg', '_module'

	def __init__(self, name, pkg_name, pkg):
		self.name = name
		self.pkg_name = pkg_name
		self.pkg = pkg
		self._module = None

	def load(self):
		if self._module is None:
			self._module = import_module(f"{self.pkg.__name__}.{self.name}.project")
			from checker21.application import app
			project_cls = app.get_project(self.name)
			if project_cls:
				project_cls._module = self
		return self._module

	def __str__(self):
		return f"{self.pkg_name}.{self.name}"

	def __repr__(self):
		return f"Project <{self.__str__()}>"
