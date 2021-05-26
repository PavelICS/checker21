from checker21.core import Checker
from checker21.utils.bash import bash


class ForbiddenFilesChecker(Checker):

	name = "files"
	verbose_name = "Forbidden files checker"
	description = "Checks if there is any forbidden file in the repository"

	def run(self, project):
		pass  # TODO code ForbiddenFilesChecker


class ForbiddenFunctionsChecker(Checker):

	name = "functions"
	verbose_name = "Forbidden functions checker"
	description = "Checks if the project uses a forbidden function"

	def run(self, project):
		self.check_executable(project)
		self.check_source_files(project)

	@staticmethod
	def check_executable(project):
		executable = "a.out"  # TODO get executable from project setup
		allowed_functions = set(project.allowed_functions)
		forbidden_functions = set()

		allowed_functions.add('__libc_start_main')

		result = bash(["nm", "-u", executable])
		functions = result.stdout
		for import_record in functions.split(b"\n"):
			import_record = import_record.strip()
			if not import_record:
				continue
			record_type, function = import_record.split(b" ", 1)
			if record_type != b"U":
				continue
			name, lib = function.split(b"@@")
			name = name.decode()
			if name not in allowed_functions:
				forbidden_functions.add(name)

		if forbidden_functions:
			print(forbidden_functions)

	def check_source_files(self, project):
		pass  # TODO check source files for forbidden functions

