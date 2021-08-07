import sys
import json
from json import JSONDecodeError
from typing import Dict, List, Optional

from checker21.utils.bash import bash
from checker21.utils.functional import cached_no_args


if sys.version_info >= (3, 8):
	from typing import TypedDict


	class OutdatedPackage(TypedDict):
		name: str
		version: str
		latest_version: str
		latest_filetype: str
else:
	OutdatedPackage = Dict


@cached_no_args
def get_outdated_packages() -> Dict[str, OutdatedPackage]:
	"""
	Searches for all outdated packages using ``pip list``
	:return: A map of outdated package name to package info
	"""
	cmd = bash([sys.executable, "-m", "pip", "list", "--outdated", "--format=json"], echo = False)
	try:
		records: List[OutdatedPackage] = json.loads(cmd.stdout.decode())
		outdated_packages = {record['name']: record for record in records}
	except JSONDecodeError:
		outdated_packages = {}
	return outdated_packages


def check_version(package_name: str) -> Optional[str]:
	"""
	Checks if there is a new available version of package
	:return: the latest package version if a new available version is found else None
	"""
	package = get_outdated_packages().get(package_name)
	return package["latest_version"] if package is not None else None
