import subprocess
import sys


def bash(command, *, echo=False):
	if echo:
		if isinstance(command, str):
			print(command)
		else:
			print(' '.join(command))

	process = subprocess.run(command, capture_output=True)
	sys.stderr.buffer.write(process.stderr)
	return process


