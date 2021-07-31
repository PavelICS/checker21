from checker21.core import Subject
from checker21.application import app
from .checkers import *


@app.register
class LibftSubject(Subject):
	check_norminette = True

	program_name = "libft.a"

	allowed_files = (
		"*.c",
		"libft.h",
		"Makefile",
	)

	allowed_functions = (
		"write",
		"malloc",
		"free",
	)

	checkers = [
		LibftUnitTestChecker(),
	]
