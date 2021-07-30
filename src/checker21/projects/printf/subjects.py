from checker21.core import Subject
from checker21.application import app


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
