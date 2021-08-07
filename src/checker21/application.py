from typing import Type, Optional, Dict, List

from checker21.conf import settings
from checker21.core import Subject, Project
from checker21.core.project import get_projects, ProjectModule


class Application:
	subjects: Dict[str, List[Type[Subject]]]
	projects: Dict[str, Type[Project]]

	active_subject = None
	subjects = {}
	projects = {}

	def get_project_modules(self) -> Dict[str, ProjectModule]:
		return get_projects()

	def get_project_module(self, name: str) -> ProjectModule:
		return self.get_project_modules()[name]

	def get_project(self, name: str) -> Optional[Type[Project]]:
		return self.projects.get(name)

	def register(self, instance: Optional[Type] = None, *, module: Optional[str] = None):
		def do_registration(_instance: Type) -> None:
			if issubclass(_instance, Project):
				self.register_project(_instance, module=module)
			if issubclass(_instance, Subject):
				self.register_subject(_instance, module=module)

		if instance is None:
			return do_registration
		do_registration(instance)
		return instance

	def _get_module_name(self, module: str) -> str:
		if module.startswith(settings.INTERNAL_PROJECTS_REPOSITORY):
			module = module[len(settings.INTERNAL_PROJECTS_REPOSITORY) + 1:]
		elif settings.EXTRA_PROJECTS_MODULE and module.startswith(settings.EXTRA_PROJECTS_MODULE):
			module = module[len(settings.EXTRA_PROJECTS_MODULE) + 1:]
		return module.split(".", 1)[0]

	def register_subject(self, subject: Type[Subject], *, module: Optional[str] = None) -> None:
		if not module:
			module = self._get_module_name(subject.__module__)
		if module not in self.subjects:
			self.subjects[module] = []
		self.subjects[module].append(subject)

	def register_project(self, project: Type[Project], *, module: Optional[str] = None) -> None:
		if not module:
			module = self._get_module_name(project.__module__)
		self.projects[module] = project

	def get_subject_classes(self, name: str) -> List[Type[Subject]]:
		if name in self.subjects:
			return self.subjects[name]

		self.subjects[name] = []
		self.get_project_module(name).load()
		return self.subjects[name]

	def get_subjects(self, name: str) -> List[Subject]:
		return [subject_cls() for subject_cls in self.get_subject_classes(name)]


app = Application()
