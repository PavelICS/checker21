import importlib

from checker21.conf import settings


class Application:
	active_project = None
	projects = {}

	def register_project(self, project):
		module = project.__module__
		if module.startswith(settings.INTERNAL_PROJECTS_REPOSITORY):
			module = module[len(settings.INTERNAL_PROJECTS_REPOSITORY) + 1:]
		module = module.split(".", 1)[0]
		if module not in self.projects:
			self.projects[module] = []
		self.projects[module].append(project)

	def get_project_classes(self, name):
		if name in self.projects:
			return self.projects[name]

		importlib.import_module(f"{settings.INTERNAL_PROJECTS_REPOSITORY}.{name}")
		return self.projects[name]

	def get_projects(self, name):
		return [project_cls() for project_cls in self.get_project_classes(name)]


app = Application()
