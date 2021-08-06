from checker21.core import Checker


class TemplateChecker(Checker):
	name = 'template-test-checker'
	verbose_name = 'Template-test-checker'
	description = 'Just a template that does nothing...'

	def run(self, project, subject):
		pass
