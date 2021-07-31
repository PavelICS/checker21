import subprocess
from subprocess import CompletedProcess
from typing import Union, List, IO, Dict


def bash(
			command: Union[str, List[str]],
			*,
			echo: bool = True,
			stdout: Union[None, int, IO] = None,
			stderr: Union[None, int, IO] = None,
			capture_output: bool = True
		) -> CompletedProcess:
	if echo:
		if isinstance(command, str):
			print(command)
		else:
			print(' '.join(command))

	options: Dict = {}
	if stdout is None and stderr is None:
		options['capture_output'] = capture_output
	else:
		options['stdout'] = stdout
		options['stderr'] = stderr

	process = subprocess.run(command, **options)
	# sys.stderr.buffer.write(process.stderr)
	return process
