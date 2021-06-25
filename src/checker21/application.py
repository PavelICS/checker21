from checker21.conf import settings
from checker21.core import Subject
from checker21.core.project import get_projects

class Application:
	active_subject = None
	subjects = {}

	def get_projects(self):
		return get_projects()

	def get_project(self, name):
		return self.get_projects()[name]

	def register(self, instance=None, *, module=None):
		def do_registration(_instance):
			if issubclass(_instance, Subject):
				self.register_subject(_instance, module=module)

		if not instance:
			return do_registration
		do_registration(instance)

	def register_subject(self, subject, *, module=None):
		if not module:
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

		self.subjects[name] = []
		self.get_project(name).load()
		return self.subjects[name]

	def get_subjects(self, name):
		return [subject_cls() for subject_cls in self.get_subject_classes(name)]


app = Application()
