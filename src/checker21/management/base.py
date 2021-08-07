import os
import sys
from io import TextIOBase
from argparse import ArgumentParser, HelpFormatter
from typing import Optional

import checker21
from checker21.conf import settings, environment
from checker21.conf.exceptions import ImproperlyConfigured
from checker21.core import Project
from checker21.projects import get_project_name
from checker21.utils.files import CurrentPath
from checker21.utils.colorize import NO_COLOR_PALETTE, get_color_style
from checker21.utils.colorize.style import NO_STYLE
from checker21.utils.pip import check_version

from .errors import CommandError, SystemCheckError


class CommandParser(ArgumentParser):
	"""
	Customized ArgumentParser class to improve some error messages and prevent
	SystemExit in several occasions, as SystemExit is unacceptable when a
	command_name is called programmatically.
	"""
	def __init__(self, *, missing_args_message=None, called_from_command_line=None, **kwargs):
		self.missing_args_message = missing_args_message
		self.called_from_command_line = called_from_command_line
		super().__init__(**kwargs)

	def parse_args(self, args=None, namespace=None):
		# Catch missing argument for a better error message
		if (self.missing_args_message and
				not (args or any(not arg.startswith('-') for arg in args))):
			self.error(self.missing_args_message)
		return super().parse_args(args, namespace)

	def error(self, message):
		if self.called_from_command_line:
			super().error(message)
		else:
			raise CommandError("Error: %s" % message)


def handle_default_options(options):
	"""
	Include any default options that all commands should accept here
	so that ManagementUtility can handle them before searching for
	user commands.
	"""
	if options.settings:
		environment.SETTINGS_MODULE = options.settings
	if options.pythonpath:
		sys.path.insert(0, options.pythonpath)


class CommandHelpFormatter(HelpFormatter):
	"""
	Customized formatter so that command_name-specific arguments appear in the
	--help output before arguments common to all commands.
	"""
	show_last = {
		'--version', '--verbosity', '--traceback', '--settings', '--pythonpath',
		'--no-color', '--force-color',
	}

	def _reordered_actions(self, actions):
		return sorted(
			actions,
			key=lambda a: set(a.option_strings) & self.show_last != set()
		)

	def add_usage(self, usage, actions, *args, **kwargs):
		super().add_usage(usage, self._reordered_actions(actions), *args, **kwargs)

	def add_arguments(self, actions):
		super().add_arguments(self._reordered_actions(actions))


class OutputWrapper(TextIOBase):
	"""
	Wrapper around stdout/stderr
	"""
	@property
	def style_func(self):
		return self._style_func

	@style_func.setter
	def style_func(self, style_func):
		if style_func and self.isatty():
			self._style_func = style_func
		else:
			self._style_func = NO_STYLE

	def __init__(self, out, ending='\n'):
		self._out = out
		self.style_func = NO_STYLE
		self.ending = ending

	def __getattr__(self, name):
		return getattr(self._out, name)

	def flush(self):
		if hasattr(self._out, 'flush'):
			self._out.flush()

	def isatty(self):
		return hasattr(self._out, 'isatty') and self._out.isatty()

	def write(self, msg='', style_func=None, ending=None):
		msg += self.ending if ending is None else ending
		style_func = style_func or self.style_func
		self._out.write(style_func(msg))


class BaseCommand:
	"""
	The base class from which all management commands ultimately
	derive.
	Use this class if you want access to all of the mechanisms which
	parse the command-line arguments and work out what code to call in
	response; if you don't need to change any of that behavior,
	consider using one of the subclasses defined in this file.
	If you are interested in overriding/customizing various aspects of
	the command_name-parsing and -execution behavior, the normal flow works
	as follows:
	1. ``manage.py`` loads the command class
		and calls its ``run_from_argv()`` method.
	2. The ``run_from_argv()`` method calls ``create_parser()`` to get
		an ``ArgumentParser`` for the arguments, parses them, performs
		any environment changes requested by options like
		``pythonpath``, and then calls the ``execute()`` method,
		passing the parsed arguments.
	3. The ``execute()`` method attempts to carry out the command_name by
		calling the ``handle()`` method with the parsed arguments; any
		output produced by ``handle()`` will be printed to standard
		output.
	4. If ``handle()`` or ``execute()`` raised any exception (e.g.
		``CommandError``), ``run_from_argv()`` will  instead print an error
		message to ``stderr``.
	Thus, the ``handle()`` method is typically the starting point for
	subclasses; many built-in commands and command_name types either place
	all of their logic in ``handle()``, or perform some additional
	parsing work in ``handle()`` and then delegate from it to more
	specialized methods as needed.
	Several attributes affect behavior at various steps along the way:
	``help``
		A short description of the command, which will be printed in
		help messages.
	``stealth_options``
		A tuple of any options the command uses which aren't defined by the
		argument parser.
	"""
	# Metadata about this command.
	help = ''
	# Makes args parser to ignore unknown args
	# and not to raise an exception
	ignore_unknown_args = False
	# A better error message when catching missing argument
	missing_args_message = None
	# Configuration shortcuts that alter various logic.
	_called_from_command_line = False
	# Arguments, common to all commands, which aren't defined by the argument parser.
	base_stealth_options = ('stderr', 'stdout')
	# Command-specific options not defined by the argument parser.
	stealth_options = ()

	def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
		self.stdout = OutputWrapper(stdout or sys.stdout)
		self.stderr = OutputWrapper(stderr or sys.stderr)
		if no_color and force_color:
			raise CommandError("'no_color' and 'force_color' can't be used together.")
		self.style = None
		if no_color:
			self.set_style(NO_COLOR_PALETTE)
		else:
			self.set_style(get_color_style(environment.COLORS, force_color))
		self.program_name = ''

	def get_version(self):
		"""
		Return the Checker21 version, which should be correct for all built-in
		commands. User-supplied commands can override this method to
		return their own version.
		"""
		return checker21.__version__

	def create_parser(self, program_name, command, **kwargs):
		"""
		Create and return the ``ArgumentParser`` which will be used to
		parse the arguments to this command_name.
		"""
		self.program_name = os.path.basename(program_name)
		parser = CommandParser(
			prog=f'{self.program_name} {command}',
			description=self.help or None,
			formatter_class=CommandHelpFormatter,
			missing_args_message=self.missing_args_message,
			called_from_command_line=getattr(self, '_called_from_command_line', None),
			**kwargs
		)
		parser.add_argument('--version', action='version', version=self.get_version())
		parser.add_argument(
			'-v', '--verbosity', default=1,
			type=int, choices=[0, 1, 2, 3],
			help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output',
		)
		parser.add_argument(
			'--settings',
			help=(
				'The Python path to a settings module, e.g. '
				'"myproject.settings". If this isn\'t provided, the '
				f'{environment.Vars.SETTINGS_MODULE} environment variable will be used.'
			),
		)
		parser.add_argument(
			'--pythonpath',
			help='A directory to add to the Python path, e.g. "/home/projects/myproject".',
		)
		parser.add_argument('--traceback', action='store_true', help='Raise on CommandError exceptions')
		parser.add_argument(
			'--no-color', action='store_true',
			help="Don't colorize the command output.",
		)
		parser.add_argument(
			'--force-color', action='store_true',
			help='Force colorization of the command output.',
		)
		self.add_arguments(parser)
		return parser

	def add_arguments(self, parser):
		"""
		Entry point for subclassed commands to add custom arguments.
		"""
		pass

	def print_help(self, program_name, command_name):
		"""
		Print the help message for this command_name, derived from
		``self.usage()``.
		"""
		parser = self.create_parser(program_name, command_name)
		parser.print_help()

	def run_from_argv(self, argv):
		"""
		Set up any environment changes requested (e.g., Python path
		and Checker21 settings), then run this command_name. If the
		command_name raises a ``CommandError``, intercept it and print it sensibly
		to stderr. If the ``--traceback`` option is present or the raised
		``Exception`` is not ``CommandError``, raise it.
		"""
		self._called_from_command_line = True

		options = self.parse_args(argv)
		cmd_options = vars(options)
		# Move positional args out of options to mimic legacy optparse
		args = cmd_options.pop('args', ())
		handle_default_options(options)
		try:
			self.execute(*args, **cmd_options)
		except CommandError as e:
			if options.traceback:
				raise

			# SystemCheckError takes care of its own formatting.
			if isinstance(e, SystemCheckError):
				self.stderr.write(str(e), NO_STYLE)
			else:
				self.stderr.write(f'{e.__class__.__name__}: {e}')
			sys.exit(e.returncode)

	def parse_args(self, argv):
		parser = self.create_parser(argv[0], argv[1])
		if self.ignore_unknown_args:
			return parser.parse_known_args(argv[2:])[0]
		else:
			return parser.parse_args(argv[2:])

	def execute(self, *args, **options):
		"""
		Try to execute this command_name
		"""
		if options['force_color'] and options['no_color']:
			raise CommandError("The --no-color and --force-color options can't be used together.")
		if options.get('stdout'):
			self.stdout = OutputWrapper(options['stdout'])
		if options.get('stderr'):
			self.stderr = OutputWrapper(options['stderr'])
		if options['force_color']:
			self.set_style(get_color_style(environment.COLORS, force_color=True))
		elif options['no_color']:
			self.set_style(NO_COLOR_PALETTE)

		# self._check_version()
		output = self.handle(*args, **options)
		return output

	def set_style(self, style):
		self.style = style
		self.stderr.style_func = self.style.ERROR

	def handle(self, *args, **options):
		"""
		The actual logic of the command_name. Subclasses must implement
		this method.
		"""
		raise NotImplementedError('subclasses of BaseCommand must provide a handle() method')

	def _check_version(self):
		new_version = check_version('checker21')
		if new_version:
			self.stdout.write(self.style.WARNING(f"New version {new_version} of checker21 is available!"))


class LabelCommand(BaseCommand):
	"""
	A management command which takes one or more arbitrary arguments
	(labels) on the command line, and does something with each of
	them.
	Rather than implementing ``handle()``, subclasses must implement
	``handle_label()``, which will be called once for each label.
	If the arguments should be names of available projects, use
	``ProjectCommand`` instead.
	"""
	label = 'label'
	missing_args_message = f"Enter at least one {label}."

	def add_arguments(self, parser):
		parser.add_argument('args', metavar=self.label, nargs='+')

	def handle(self, *labels, **options):
		output = []
		for label in labels:
			label_output = self.handle_label(label, **options)
			if label_output:
				output.append(label_output)
		return '\n'.join(output)

	def handle_label(self, label, **options):
		"""
		Perform the command's actions for ``label``, which will be the
		string as given on the command line.
		"""
		raise NotImplementedError('subclasses of LabelCommand must provide a handle_label() method')


class ProjectCommand(BaseCommand):
	"""
	A management command which takes one project name as
	argument, and does something with it.
	Rather than implementing ``handle()``, subclasses must implement
	``handle_project()``, which will be called once for each label.
	"""
	project_required: bool
	project_required = True

	def create_parser(self, program_name, command, **kwargs):
		if self.project_required:
			self.missing_args_message = "Enter a project name."
		return super().create_parser(program_name, command, **kwargs)

	def add_arguments(self, parser) -> None:
		options = {
			'help':     'A project for which the command will be executed.',
		}
		if not self.project_required:
			options['nargs'] = '?'
		parser.add_argument('project', **options)
		parser.add_argument('-p', '--path', help='Path to the project, e.g. "/home/delyn/libft"', default='.')

	def handle(self, *args, **options) -> None:
		project_cls = None
		project_name = options.pop('project', None)

		if project_name:
			from checker21.application import app
			try:
				standard_project_name = get_project_name(project_name)
				project_module = app.get_project_module(standard_project_name)
			except KeyError:
				self.stderr.write(f'Project "{project_name}" is not found!')
				return

			project_name = standard_project_name
			project_module.load()
			project_cls = app.get_project(project_name)

		project = None
		project_path = CurrentPath(options.get('path')).resolve()
		if project_path.exists():
			if project_cls is None:
				self.stderr.write(f'Project module "{project_name}" has no `Project` class!')
				return
			temp_folder = self._resolve_project_temp_path(project_path)
			project = project_cls(project_path, temp_folder)
		elif self.program_name:
			self.stderr.write(f'Project path "{project_path}" does not exist!')
			return

		if project is not None:
			with project.path:
				self.handle_project(project, **options)
		else:
			self.handle_project_not_found(project_name, **options)

	def handle_project(self, project: Project, **options) -> None:
		"""
		Perform the command's actions for ``project``, which will be
		the Project instance parsed from the command line.
		The method ``handle_project()`` is run in the project directory.
		"""
		raise NotImplementedError('subclasses of ProjectCommand must provide a handle_project() method')

	def handle_project_not_found(self, project_name: Optional[str], **options) -> None:
		"""
		Perform the command's actions for ``project``, which will be the
		string as given on the command line validated as not existing project.
		"""
		pass

	def _resolve_project_temp_path(self, project_path) -> CurrentPath:
		"""
			Validates and returns project_temp_path
			Depends on ``settings.PROJECT_TEMP_FOLDER``
		"""
		temp_folder: str = settings.PROJECT_TEMP_FOLDER
		if temp_folder.startswith("/"):
			raise ImproperlyConfigured("The abstract path for the PROJECT_TEMP_FOLDER currently is not supported!")
		temp_folder = temp_folder.replace('./', '').strip('/')
		if '/' in temp_folder:
			raise ImproperlyConfigured("The PROJECT_TEMP_FOLDER should contain only one level folder")

		temp_path = (project_path / temp_folder).resolve()
		if not temp_path.exists():
			temp_path.mkdir()
		return temp_path
