import functools
import os
import sys
from argparse import _StoreConstAction, _AppendConstAction, _SubParsersAction, _CountAction
from importlib import import_module
from pathlib import Path
import pkgutil
from difflib import get_close_matches
from typing import Union, List, Optional, Dict, Iterable, cast
from os import PathLike

import checker21
from checker21.conf import settings

from .base import BaseCommand, CommandParser, handle_default_options
from .errors import CommandError
from checker21.conf.exceptions import ImproperlyConfigured


def find_commands(commands_dir: Union[str, PathLike]):
    """
    Given a path to a management directory, return a list of all the command_name
    names that are available.
    """
    command_dir = Path(commands_dir)
    return [
        name
        for _, name, is_pkg in pkgutil.iter_modules([command_dir])
        if not is_pkg and not name.startswith('_')
    ]


def load_command_class(module_name: str, name: str):
    """
    Given a command name and a module name, return the Command
    class instance. Allow all errors raised by the import process
    (ImportError, AttributeError) to propagate.
    """
    if module_name == 'checker21':
        module_name = 'checker21.management.commands'
    module = import_module(f'{module_name}.{name}')
    return module.Command()


@functools.lru_cache(maxsize=None)
def get_commands() -> Dict[str, str]:
    """
    Return a dictionary mapping command names to their callback module.
    Core commands are always included. If a settings module has been
    specified, also include user-defined commands.
    The dictionary is in the format {command_name: module_name}. Key-value
    pairs from this dictionary can then be used in calls to
    load_command_class(module_name, command_name)
    The dictionary is cached on the first call and reused on subsequent
    calls.
    """
    core_commands_dir = Path(__path__[0]) / 'commands'
    commands = {
        name: 'checker21'
        for name in find_commands(core_commands_dir)
    }

    if not settings.configured:
        return commands

    if settings.EXTRA_COMMANDS_MODULE:
        extra_module = import_module(str(settings.EXTRA_COMMANDS_MODULE))
        commands.update({
            name: extra_module.__name__
            for name in find_commands(extra_module.__path__[0])
        })

    return commands


def fetch_command(command_name: str):
    """
    Fetch the given command_name,
    throwing CommandError if it can't be found.
    """
    # Load the command object by name.
    module_name = get_commands().get(command_name)
    if module_name is None:
        raise CommandError(f"Unknown command: {repr(command_name)}.")
    if isinstance(module_name, BaseCommand):
        # If the command is already loaded, use it directly.
        _class = module_name
    else:
        _class = load_command_class(module_name, command_name)
    return _class


# noinspection PyProtectedMember
def call_command(command_name: str, *args, program_name=None, **options):
    """
    Call the given command, with the given options and args/kwargs.
    This is the primary API you should use for calling specific commands.
    `command_name` may be a string or a command object. Using a string is
    preferred unless the command object is required for further processing or
    testing.
    Some examples:
        call_command('version')
        call_command('shell', plain=True)
        call_command('run', 'libft')
        from checker21.management.commands import run
        cmd = run.Command()
        call_command(cmd, 'libft', verbosity=0, interactive=False)
        # Do something with cmd ...
    """
    if isinstance(command_name, BaseCommand):
        # Command object passed in.
        command = command_name
        command_name = command.__class__.__module__.split('.')[-1]
    else:
        command = fetch_command(command_name)

    # Simulate argument parsing to get the option defaults
    program_name = program_name or ''
    parser = command.create_parser(program_name, command_name)
    # Use the `dest` option name from the parser option
    opt_mapping = {
        min(s_opt.option_strings).lstrip('-').replace('-', '_'): s_opt.dest
        for s_opt in parser._actions if s_opt.option_strings
    }
    arg_options = {opt_mapping.get(key, key): value for key, value in options.items()}
    parse_args = []
    for arg in args:
        if isinstance(arg, (list, tuple)):
            parse_args += map(str, arg)
        else:
            parse_args.append(str(arg))

    # noinspection PyShadowingNames,PyProtectedMember
    def get_actions(parser):
        # Parser actions and actions from sub-parser choices.
        for opt in parser._actions:
            if isinstance(opt, _SubParsersAction):
                for sub_opt in opt.choices.values():
                    yield from get_actions(sub_opt)
            else:
                yield opt

    parser_actions = list(get_actions(parser))
    mutually_exclusive_required_options = {
        opt
        for group in parser._mutually_exclusive_groups
        for opt in group._group_actions if group.required
    }
    # Any required arguments which are passed in via **options must be passed
    # to parse_args().
    for opt in parser_actions:
        if (
            opt.dest in options and
            (opt.required or opt in mutually_exclusive_required_options)
        ):
            parse_args.append(min(opt.option_strings))
            if isinstance(opt, (_AppendConstAction, _CountAction, _StoreConstAction)):
                continue
            value = arg_options[opt.dest]
            if isinstance(value, (list, tuple)):
                parse_args += map(str, value)
            else:
                parse_args.append(str(value))
    defaults = parser.parse_args(args=parse_args)
    defaults = dict(defaults._get_kwargs(), **arg_options)
    # Raise an error if any unknown options were passed.
    stealth_options = set(command.base_stealth_options + command.stealth_options)
    dest_parameters = {action.dest for action in parser_actions}
    valid_options = (dest_parameters | stealth_options).union(opt_mapping)
    unknown_options = set(options) - valid_options
    if unknown_options:
        raise TypeError(
            "Unknown option(s) for %s command: %s. "
            "Valid options are: %s." % (
                command_name,
                ', '.join(sorted(unknown_options)),
                ', '.join(sorted(valid_options)),
            )
        )
    # Move positional args out of options to mimic legacy optparse
    args = defaults.pop('args', ())
    return command.execute(*args, **defaults)


def get_possible_command_matches(command_name: str, commands: Iterable[str]) -> List[str]:
    possible_matches = [command for command in commands if command.startswith(command_name)]
    close_matches = [x for x in get_close_matches(command_name, commands) if x not in possible_matches]
    return possible_matches + cast(List[str], close_matches)


def get_program_name(path: str) -> str:
    program_name = os.path.basename(path)
    if program_name == '__main__.py':
        program_name = 'python -m checker21'
    return program_name


class ManagementUtility:
    """
    Encapsulate the logic of the manage.py utilities.
    """
    argv: List[str]
    program_name: str
    settings_exception: Optional[Exception]

    def __init__(self, argv: Optional[List[str]] = None):
        self.argv = argv or sys.argv[:]
        self.program_name = get_program_name(self.argv[0])
        self.settings_exception = None

    def execute(self):
        """
        Given the command_name-line arguments, figure out which command_name is being
        run, create a parser appropriate to that command_name, and run it.
        """
        if len(self.argv) == 1:
            # Display help if no arguments were given.
            self.argv = [self.argv[0], 'help']

        command_name = self.argv[1]

        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = CommandParser(
            prog            = self.program_name,
            usage           = '%(prog)s command_name [options] [args]',
            add_help        = False,
            allow_abbrev    = False,
        )
        parser.add_argument('--settings')
        parser.add_argument('--pythonpath')
        parser.add_argument('args', nargs='*')  # catch-all
        try:
            options, args = parser.parse_known_args(self.argv[2:])
            handle_default_options(options)
        except CommandError:
            pass  # Ignore any option errors at this point.

        try:
            checker21.setup()
        except ImproperlyConfigured as exc:
            self.settings_exception = exc
        except ImportError as exc:
            self.settings_exception = exc

        try:
            command = fetch_command(command_name)
            argv = self.argv
        except CommandError:
            command = fetch_command('help')
            argv = [self.argv[0], 'help', *self.argv[1:]]

        command.run_from_argv(argv)


def execute_from_command_line(argv=None):
    """Run a ManagementUtility."""
    utility = ManagementUtility(argv)
    utility.execute()
