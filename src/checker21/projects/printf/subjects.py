from checker21.core import Subject
from checker21.application import app
from .checkers import *


@app.register
class PrintfSubject(Subject):
	check_norminette = True

	program_name = "libftprintf.a"

	allowed_files = (
		"*.c",
		"*.h",
		"*/*.c",
		"*/*.h",
		"Makefile",
		"*/Makefile",
	)

	allowed_functions = (
		"write",
		"malloc",
		"free",
		"va_start",
		"va_arg",
		"va_copy",
		"va_end",
	)

	checkers = [
		PftChecker(),
	]


@app.register
class PrintfSubjectBonus(Subject):
	bonus = True

	checkers = [
		PftChecker(),
	]
