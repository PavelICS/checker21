from checker21.core import Subject
from checker21.application import app
from .checkers import *


@app.register
class GnlSubject(Subject):
	check_norminette = True

	allowed_files = (
		"get_next_line(_bonus)?.c",
		"get_next_line_utils(_bonus)?.c",
		"get_next_line(_bonus)?.h",
	)

	allowed_functions = (
		"read",
		"malloc",
		"free",
	)

	checkers = [
		GnlWarMachineChecker(),
		# GnlKillerChecker(),
	]
