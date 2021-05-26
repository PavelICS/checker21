from checker21.core import Project


class LibftProject(Project):

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
