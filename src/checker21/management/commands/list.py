from checker21.management.base import BaseCommand
from checker21.application import app

class Command(BaseCommand):
	help = 'Lists all available projects'

	def handle(self, *args, **options):
		verbosity = options.get('verbosity')
		self.print_projects_list(verbosity)

	def print_projects_list(self, verbosity=1):
		"""Prints the list of all available projects."""

		if verbosity == 0:
			for project_name in sorted(app.get_projects()):
				self.stdout.write(self.format_project_name(project_name))

		else:
			self.stdout.write("")
			self.stdout.write("Available projects:")
			self.stdout.write("")
			for project_name in sorted(app.get_projects()):
				self.stdout.write(f"    {self.format_project_name(project_name)}")

	def format_project_name(self, project_name):
		aliases = self.get_aliases(project_name)
		if aliases:
			project_name = f'{project_name} / {"/".join(aliases)}'
		return project_name

	def get_aliases(self, project_name):
		from checker21.projects import aliases
		return sorted([
			key
			for key, value in aliases.items()
			if value == project_name
		])
