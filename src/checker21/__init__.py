from pathlib import Path

from checker21.utils.version import get_version, Version

VERSION = Version((0, 2, 0, 'alpha'))

__version__ = get_version(VERSION)


def setup():
	"""
		Configure the settings (this happens as a side effect of accessing the first setting).
		Configure logging. # TODO
	"""
	from checker21.conf import settings
	# noinspection PyStatementEffect
	settings.INTERNAL_PROJECTS_REPOSITORY


CHECKER21_FILE_CONTENT = b"""
# Setting PATH for Python 3.7
HOME_DIR=`dirname ~/any`
PATH="${HOME_DIR}/Library/Python/3.7/bin:${PATH}"
export PATH
"""


def install_macos():
	print("Installing ``~/.checker21`` script")
	with (Path.home() / ".checker21").open("wb") as f:
		f.write(CHECKER21_FILE_CONTENT)
