class CommandError(Exception):
	"""
	Exception class indicating a problem while executing a management
	command_name.
	If this exception is raised during the execution of a management
	command_name, it will be caught and turned into a nicely-printed error
	message to the appropriate output stream (i.e., stderr); as a
	result, raising this exception (with a sensible description of the
	error) is the preferred way to indicate that something has gone
	wrong in the execution of a command_name.
	"""
	def __init__(self, *args, returncode=1, **kwargs):
		self.returncode = returncode
		super().__init__(*args, **kwargs)


class SystemCheckError(CommandError):
	"""
	The system check framework detected unrecoverable errors.
	"""
	pass
