from typing import Optional, Tuple, NewType

Version = NewType('Version', Tuple[int, int, int, str])


def get_version(version: Optional[Version] = None) -> str:
	"""Return a PEP 440-compliant version number from VERSION."""
	version = get_complete_version(version)

	# Now build the two parts of the version number:
	# main = X.Y[.Z]
	# sub = {a|b|rc}N - for alpha, beta, and rc releases

	main = get_main_version(version)

	sub = ''
	if version[3] != 'final':
		mapping = {'alpha': 'a', 'beta': 'b', 'rc': 'rc'}
		sub = mapping[version[3]]

	return main + sub


def get_main_version(version: Optional[Version] = None) -> str:
	"""Return main version (X.Y[.Z]) from VERSION."""
	version = get_complete_version(version)
	parts = 2 if version[2] == 0 else 3
	return '.'.join(str(x) for x in version[:parts])


def get_complete_version(version: Optional[Version] = None) -> Version:
	"""
	Return a tuple of the checker21 version. If version argument is non-empty,
	check for correctness of the tuple provided.
	"""
	if version is None:
		# noinspection PyPep8Naming
		from checker21 import VERSION
		return VERSION
	else:
		assert len(version) == 4
		assert version[3] in ('alpha', 'beta', 'rc', 'final')
		return version
