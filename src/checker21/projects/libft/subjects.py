from checker21.core import Subject


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
