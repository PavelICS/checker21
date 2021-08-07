import os
from pathlib import Path
from typing import Union, Tuple, Iterable

import checker21
from checker21.management import BaseCommand


class Command(BaseCommand):
	help = 'Creates an environment for developing checkers for a new project'

	checker21_path = Path(checker21.__path__[0])

	def add_arguments(self, parser):
		parser.add_argument('project_name',
			help='New project name',
			metavar='project name',
			nargs = '?',
			default = '',
		)

	def handle(self, *args, **options):
		os.chdir("/Users/delyn/CLionProjects/testing_projects/test0")
		target = Path("settings.py")
		if target.exists():
			self.stderr.write("Another settings file already exists!\n"
								"Cannot start a new project")
			return

		self.copy_settings(target)
		self.create_package("commands")
		project_pkg = self.create_package("projects")
		project_name = options.get('project_name')
		if project_name:
			self.create_project(project_name, project_pkg)
		self.stdout.write(self.style.SUCCESS("A new project environment is created!"))

	def copy_settings(self, target: Path) -> None:
		source = self.checker21_path / 'conf/default_settings.py'
		with source.open('rb') as f:
			data = f.read()
		data = data.replace(b"EXTRA_COMMANDS_MODULE = None", b'EXTRA_COMMANDS_MODULE = "commands"')
		data = data.replace(b"EXTRA_PROJECTS_MODULE = None", b'EXTRA_PROJECTS_MODULE = "projects"')
		with target.open('wb') as f:
			f.write(data)

	def create_package(self, dir_name: Union[Path, str]) -> Path:
		pkg = Path(dir_name)
		pkg.mkdir(exist_ok=True)
		(pkg / "__init__.py").touch(exist_ok=True)
		return pkg

	def create_project(self, project_name: str, pkg: Path) -> None:
		project_dir = pkg / project_name
		project_dir.mkdir(exist_ok=True)
		self.copy_project_init_file(project_name, project_dir)
		self.copy_project_file(project_name, project_dir)
		self.copy_subjects_file(project_name, project_dir)
		self.copy_checkers_file(project_name, project_dir)

	def copy_project_file(self, project_name: str, project_dir: Path) -> None:
		target = project_dir / "project.py"
		if target.exists():
			return
		self.copy_template("project.py", target, [
			(b"{{project_name}}", project_name.encode())
		])

	def copy_subjects_file(self, project_name: str, project_dir: Path) -> None:
		target = project_dir / "subjects.py"
		if target.exists():
			return
		self.copy_template("subjects.py", target)

	def copy_checkers_file(self, project_name: str, project_dir: Path) -> None:
		target = project_dir / "checkers.py"
		if target.exists():
			return
		self.copy_template("checkers.py", target)

	def copy_project_init_file(self, project_name: str, project_dir: Path) -> None:
		target = project_dir / "__init__.py"
		if target.exists():
			return
		self.copy_template("__init__.py", target)

	def copy_template(self, template_name: str, target: Path, replaces: Iterable[Tuple[bytes, bytes]] = ()) -> None:
		source = self.checker21_path / "templates/project" / template_name
		with source.open('rb') as f:
			data = f.read()
		for record in replaces:
			data = data.replace(*record)
		with target.open('wb') as f:
			f.write(data)
