from checker21.core import Subject
from checker21.application import app


@app.register
class LibftSubject(Subject):

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
