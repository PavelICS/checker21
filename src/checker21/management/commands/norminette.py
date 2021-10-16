import re
from pathlib import Path
from typing import Set, Dict, Callable, Any, List

from checker21.core import Project
from checker21.management import AnonymousProjectCommand
from checker21.utils.code_fixer import CodeFixer
from checker21.utils.norminette import NorminetteCheckStatus, Norminette, NorminetteError


class Command(AnonymousProjectCommand):
	help = 'Runs norminette related tasks'
	state_filename: str = "norminette.json"

	_norminette: Norminette

	basic_subcommands: Set[str] = {
		"version",
	}
	basic_subcommands_alt_names: Dict[str, str] = {
		"v": "version",
	}
	subcommands: Set[str] = {
		"check", "errors", "all", "clear", "fix",
	}
	subcommands_alt_names: Dict[str, str] = {
		"re": "all",
	}

	def add_arguments(self, parser):
		super().add_arguments(parser)
		parser.add_argument(
			'subcommand',
			help='What norminette should do. By default check files by norm.',
			metavar='command',
			nargs='?',
			default='',
		)

	def get_basic_subcommand(self, subcommand_name: str) -> Callable[[Dict], None]:
		subcommand_name = subcommand_name.lower()
		subcommand_name = self.basic_subcommands_alt_names.get(subcommand_name, subcommand_name)
		if subcommand_name in self.basic_subcommands:
			return getattr(self, f"handle_{subcommand_name}")

	def get_subcommand(self, subcommand_name: str) -> Callable[[Project, Dict], None]:
		if not subcommand_name:
			# by default return check handler
			return self.handle_check
		subcommand_name = subcommand_name.lower()
		subcommand_name = self.subcommands_alt_names.get(subcommand_name, subcommand_name)
		if subcommand_name in self.subcommands:
			return getattr(self, f"handle_{subcommand_name}")

	def handle(self, *args, **options) -> None:
		subcommand_name: str = options.pop("subcommand", "")
		basic_subcommand = self.get_basic_subcommand(subcommand_name)
		if basic_subcommand:
			self._norminette = Norminette()
			basic_subcommand(**options)
			return

		subcommand = self.get_subcommand(subcommand_name)
		if not subcommand:
			self.stderr.write(f'Unknown norminette command: "{subcommand_name}"!')
			return

		project_path = self._resolve_project_path(options)
		if not project_path:
			return
		temp_folder = self._resolve_project_temp_path(project_path)
		project = Project(project_path, temp_folder)
		with project.path:
			self._norminette = self.load_norminette(project)
			subcommand(project, **options)

	@property
	def norminette(self):
		return self._norminette

	def load_norminette(self, project: Project):
		return Norminette.load(project.temp_folder / self.state_filename)

	def handle_version(self, **options):
		if self.norminette.version is None:
			self.stdout.write(self.style.ERROR("Norminette is not found!"))
			return
		self.stdout.write(self.style.INFO(f"Using norminette {self.norminette.version}"))

	def handle_check(
			self,
			project: Project,
			*,
			only_errors: bool = False,
			only_new: bool = False,
			**options
	) -> None:
		self.handle_version(**options)
		if not self.norminette.version:
			return

		result = self.norminette.check_project(project)
		self.norminette.save()
		if not only_new:
			result = self.norminette.state.result

		if not result:
			self.stdout.write(self.style.INFO("Nothing has changed!"))
			return

		if only_errors:
			result = {key: info for key, info in result.items() if info["status"] != NorminetteCheckStatus.OK}
		self.print_result(result)

	def handle_errors(self, project: Project, **options) -> None:
		self.handle_check(project, only_errors=True, **options)

	def print_result(self, result) -> None:
		if not result:
			self.stdout.write(self.style.SUCCESS("OK"))
			return

		for file, info in result.items():
			status = info["status"]

			if status == NorminetteCheckStatus.OK:
				self.stdout.write(self.style.SUCCESS(info["line"]))

			elif status == NorminetteCheckStatus.NOT_VALID:
				self.stdout.write(self.style.WARNING(info["line"]))

			elif status == NorminetteCheckStatus.ERROR:
				self.stdout.write(self.style.ERROR(info["line"]))
				for error in info["errors"]:
					self.stdout.write(error)

			if "warnings" in info:
				for warning in info["warnings"]:
					self.stdout.write(self.style.WARNING(warning))

	def handle_clear(self, project: Project, **options) -> None:
		try:
			self.norminette.state.path.unlink()
		except FileNotFoundError:
			pass
		self.stdout.write(self.style.INFO("The norminette cache has been cleared!"))

	def handle_all(self, project: Project, **options) -> None:
		self.handle_clear(project)
		self.handle_check(project)

	def handle_fix(self, project: Project, **options) -> None:
		login = "delyn"
		email = f"{login}@student.21-school.ru"

		self.stdout.write(self.style.INFO("Trying to fix cached errors..."))
		result = self.norminette.state.result
		for file, info in result.items():
			status = info["status"]

			if status != NorminetteCheckStatus.ERROR:
				continue

			errors_to_fix: List[NorminetteError] = []
			has_empty_line_first = False
			for error in info["errors"]:
				_error = NorminetteError.parse(error)
				if _error:
					if _error.code in {"INVALID_HEADE", }:
						errors_to_fix.append(_error)
					elif _error.code == "EMPTY_LINE_FILE_START":
						has_empty_line_first = True
						errors_to_fix.append(_error)
					elif _error.code == "INVALID_HEADER":
						if not has_empty_line_first:
							errors_to_fix.append(_error)

			if errors_to_fix:
				path = Path(file)
				if not path.exists():
					continue
				self.stdout.write(self.style.INFO(f'Trying to fix errors in {file}'))
				code_fixer = CodeFixer(path)
				for error in errors_to_fix:
					self.stdout.write(f"Fixing {error.raw}")
					if error.code == "EMPTY_LINE_FILE_START":
						code_fixer.delete_file_leading_spaces()
					elif error.code == "INVALID_HEADER":
						if not has_empty_line_first:
							code_fixer.insert_header(login, email)
				code_fixer.save()

		self.handle_check(project)
