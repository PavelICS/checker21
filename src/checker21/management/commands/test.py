from checker21.application import app
from checker21.management.base import ProjectCommand


class Command(ProjectCommand):
	help = 'A test command'

	def add_arguments(self, parser):
		super().add_arguments(parser)
		parser.add_argument('checker_name',
		                    help='Which check to run. By default runs all checks.',
		                    metavar='check name',
		                    nargs= '?'
		)

	def handle_project(self, project, **options):
		self.stdout.write(self.style.INFO(f"Start testing {project}"))

		check_name = options.get('checker_name') or 'all'
		for subject in app.get_subjects(project):
			self.stdout.write(f'Subject: {subject}')
			for checker in subject.get_checkers():
				if check_name == 'all' or check_name == checker.name:
					self.stdout.write(f'Checker: {checker}')
					checker(subject)
