import importlib

from checker21.conf import settings


class Application:
	active_subject = None
	subjects = {}

	def register_subject(self, subject):
		module = subject.__module__
		if module.startswith(settings.INTERNAL_PROJECTS_REPOSITORY):
			module = module[len(settings.INTERNAL_PROJECTS_REPOSITORY) + 1:]
		module = module.split(".", 1)[0]
		if module not in self.subjects:
			self.subjects[module] = []
		self.subjects[module].append(subject)

	def get_subject_classes(self, name):
		if name in self.subjects:
			return self.subjects[name]

		importlib.import_module(f"{settings.INTERNAL_PROJECTS_REPOSITORY}.{name}")
		return self.subjects[name]

	def get_subjects(self, name):
		return [subject_cls() for subject_cls in self.get_subject_classes(name)]


app = Application()
