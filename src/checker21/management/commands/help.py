from collections import defaultdict

import checker21
from checker21.conf import environment, settings
from checker21.conf.exceptions import ImproperlyConfigured
from checker21.management import get_commands, fetch_command, CommandError, get_possible_command_matches
from checker21.management.base import BaseCommand


class Command(BaseCommand):
	help = 'Usage help. This lists all current command line options with a short description.'

	ignore_unknown_args = True
	settings_exception = None

	def add_arguments(self, parser):
		parser.add_argument('command',
			help='Shows help on a specific command.',
			metavar='command',
			nargs = '?',
			default = '',
		)

	def handle(self, *args, **options):
		try:
			checker21.setup()
		except ImproperlyConfigured as exc:
			self.settings_exception = exc
		except ImportError as exc:
			self.settings_exception = exc
		command_name = options.get('command')
		verbosity = options.get('verbosity')
		if command_name:
			self.print_command_help_text(command_name)
		else:
			self.print_help_text(verbosity)

	def print_help_text(self, verbosity=1):
		"""Prints the script's main help text."""
		if verbosity == 0:
			# Show only commands names list
			self.stdout.write('\n'.join(sorted(get_commands().keys())))
			return

		usage = [
			"",
			f"Type '{self.program_name} help <command>' for help on a specific command.",
			"",
			"Available commands:",
		]
		commands_dict = defaultdict(lambda: [])
		for name, app in get_commands().items():
			# app = app.rpartition('.')[-1]
			commands_dict[app].append(name)
		# style = get_color_style(environment.COLORS)
		for app in sorted(commands_dict):
			usage.append("")
			usage.append(self.style.NOTICE(f"[{app}]"))
			if verbosity > 1:
				for name in sorted(commands_dict[app]):
					usage.append(self.style.SUCCESS(f"====>  {name}  <===="))
					try:
						command = fetch_command(name)
					except Exception as exc:
						usage.append(self.style.ERROR(str(exc)))
					else:
						usage.append(command.help)
					usage.append("")
			else:
				for name in sorted(commands_dict[app]):
					usage.append(f"    {name}")
		usage.append("")
		# Output an extra note if settings are not properly configured
		if self.settings_exception is not None:
			usage.append(self.style.NOTICE(
				"Note that only Checker21 core commands are listed "
				"as settings are not properly configured (error: %s)."
				% self.settings_exception))
		self.stdout.write('\n'.join(usage))

	def print_command_help_text(self, command_name):
		"""
		Try to fetch the given command_name, printing a message with the
		appropriate command_name called from the command_name line (usually
		"checker.py") if it can't be found.
		"""
		try:
			command = fetch_command(command_name)
		except CommandError:
			if environment.SETTINGS_MODULE:
				# If `command_name` is missing due to misconfigured settings, the
				# following line will retrigger an ImproperlyConfigured exception
				# (get_commands() swallows the original one) so the user is
				# informed about it.
				checker21.setup()
			elif not settings.configured:
				self.stderr.write("No Checker21 settings specified.")
			possible_matches = get_possible_command_matches(command_name, get_commands())
			self.stderr.write(f"Unknown command: {repr(command_name)}.", ending = '')
			if possible_matches:
				self.stderr.write(f" Did you mean {possible_matches[0]}?")
			else:
				self.stderr.write("")
			if len(possible_matches) > 1:
				self.stderr.write("Similar commands:")
				similar_commands = "\n  ".join(possible_matches)
				self.stderr.write(f"  {similar_commands}")
			self.stderr.write(f"Type '{self.program_name} help' for usage.")
			return
		command.print_help(self.program_name, command_name)
