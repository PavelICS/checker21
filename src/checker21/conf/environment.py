import os
import sys
from typing import Any


class Vars:
	SETTINGS_MODULE = "CHECKER21_SETTINGS_MODULE"
	COLORS          = "CHECKER21_COLORS"

	def __getattr__(self, name: str) -> str:
		if name in os.environ:
			return name
		raise AttributeError(f"'{name}' isn't registered as an environment variable")


_environment = sys.modules[__name__]


def __getattr__(name: str) -> Any:
	var = getattr(Vars, name)
	value = os.environ.get(var)
	# cache it
	setattr(_environment, var, value)
	return value
