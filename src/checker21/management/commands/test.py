from checker21.management.base import ProjectCommand
from checker21.utils.text_format import align_line

CONSOLE_WIDTH = 92
BLANK_LINE = '-' * CONSOLE_WIDTH


class Command(ProjectCommand):
	help = 'A test command'

	def add_arguments(self, parser):
		super().add_arguments(parser)
		parser.add_argument(
			'checker_name',
			help    = 'Check to run. By default runs all checks.',
			metavar = 'check name',
			nargs   = '?'
		)

	def handle_project(self, project, **options):
		self.stdout.write(self.style.INFO(f"Start testing {project.verbose_name}"))

		check_name = options.get('checker_name') or 'all'
		started_checkers_count = 0
		for subject in project.get_subjects():
			subject_class_name = str(subject.__class__).split('.')[-1].split("'")[0]
			self.stdout.write(f'Subject: {subject_class_name}')
			for checker in subject.get_checkers():
				if check_name == 'all' or check_name == checker.name:
					started_checkers_count += 1
					self.run_checker(checker, project, subject)
			self.stdout.write(self.style.INFO(BLANK_LINE))

		if started_checkers_count == 0:
			self.stderr.write(f"Checker `{check_name}` is not found!")

	def run_checker(self, checker, project, subject):
		self.print_checker_name(checker)
		checker.init_io(self.stdout, self.stderr, self.style)
		checker(project, subject)

	def print_checker_name(self, checker):
		self.stdout.write(self.style.INFO(BLANK_LINE))
		name = align_line(str(checker), CONSOLE_WIDTH)
		name = f'|{name[1:-1]}|'
		self.stdout.write(self.style.INFO(name))
		self.stdout.write(self.style.INFO(BLANK_LINE))
