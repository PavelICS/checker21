from checker21.utils.version import get_version

VERSION = (0, 0, 3, 'alpha')

__version__ = get_version(VERSION)


def setup():
	"""
		Configure the settings (this happens as a side effect of accessing the first setting).
		Configure logging. # TODO
	"""
	from checker21.conf import settings
	# noinspection PyStatementEffect
	settings.INTERNAL_PROJECTS_REPOSITORY