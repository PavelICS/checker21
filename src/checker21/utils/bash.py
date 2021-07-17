import subprocess
import sys


def bash(command, *, echo=True, stdout=None, stderr=None, capture_output=True):
	if echo:
		if isinstance(command, str):
			print(command)
		else:
			print(' '.join(command))

	options = {}
	if stdout is None and stderr is None:
		options['capture_output'] = capture_output
	else:
		options['stdout'] = stdout
		options['stderr'] = stderr

	process = subprocess.run(command, **options)
	# sys.stderr.buffer.write(process.stderr)
	return process


