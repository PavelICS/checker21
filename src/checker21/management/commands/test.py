from checker21.application import app
from checker21.management.base import ProjectCommand
from checker21.utils.text_format import align_line

CONSOLE_WIDTH = 92
BLANK_LINE = '-' * CONSOLE_WIDTH


class Command(ProjectCommand):
	help = 'A test command'

	def add_arguments(self, parser):
		super().add_arguments(parser)
		parser.add_argument('checker_name',
							help='Which check to run. By default runs all checks.',
							metavar='check name',
							nargs='?'
		)

	def handle_project(self, project, **options):
		self.stdout.write(self.style.INFO(f"Start testing {project}"))

		check_name = options.get('checker_name') or 'all'
		for subject in app.get_subjects(project):
			subject_class_name = str(subject.__class__).split('.')[-1].split("'")[0]
			self.stdout.write(f'Subject: {subject_class_name}')
			for checker in subject.get_checkers():
				if check_name == 'all' or check_name == checker.name:
					self.run_checker(checker, subject)
			self.stdout.write(self.style.INFO(BLANK_LINE))

	def run_checker(self, checker, subject):
		self.print_checker_name(checker)
		checker.init_io(self.stdout, self.stderr, self.style)
		checker(subject)

	def print_checker_name(self, checker):
		self.stdout.write(self.style.INFO(BLANK_LINE))
		name = align_line(str(checker), CONSOLE_WIDTH)
		name = f'|{name[1:-1]}|'
		self.stdout.write(self.style.INFO(name))
		self.stdout.write(self.style.INFO(BLANK_LINE))

