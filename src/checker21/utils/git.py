from typing import List, Optional

from checker21.utils.bash import bash


def git_list_files() -> Optional[List[str]]:
	cmd = bash(['git', 'ls-files'], echo=False)
	if cmd.stderr:
		return None
	files = []
	for line in cmd.stdout.split(b'\n'):
		line = line.decode().strip()
		if line:
			files.append(line)
	return files
