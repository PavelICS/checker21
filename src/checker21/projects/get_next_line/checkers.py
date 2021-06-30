import os
import re
from pathlib import Path

from checker21.core import GitChecker
from checker21.utils.bash import bash


class GnlWarMachineChecker(GitChecker):
	name = 'gnl-war-machine'
	verbose_name = 'GNL war machine'
	description = 'Downloads gnl-war-machine-v2019 checker and runs it'

	git_url = 'https://github.com/C4r4c0l3/gnl-war-machine-v2019'
	target_dir = 'gnl-war-machine-v2019'

	def run(self, subject):
		os.chdir(self.target_dir)
		self.git_config()
		bash(['/bin/bash', 'grademe.sh'], stdout=self.stdout, stderr=self.stderr)
		os.chdir('..')

	def git_config(self):
		config = Path('my_config.sh')
		config_backup = Path('my_config.sh.backup')
		if config_backup.exists():
			return
		with config.open('rb') as f:
			data = f.read()
		with config_backup.open('wb') as f:
			f.write(data)
		with config.open('wb') as f:
			f.write(data.replace(b'../../get_next_line', b'../'))


class GnlKillerChecker(GitChecker):
	name = 'gnlkiller'
	verbose_name = 'GNL killer'
	description = 'Downloads gnlkiller checker and runs it'

	git_url = 'https://github.com/DontBreakAlex/gnlkiller'
	target_dir = 'gnlkiller'

	def run(self, subject):
		os.chdir(self.target_dir)
		self.git_config()
		bash(['/bin/bash', 'run.sh'], stdout = self.stdout, stderr = self.stderr)
		os.chdir('..')

	def git_config(self):
		bash(['cp', '../get_next_line.h', '.'])
		bash(['cp', '../get_next_line.c', '.'])
		bash(['cp', '../get_next_line_utils.c', '.'])

		config = Path('run.sh')
		config_backup = Path('run.sh.backup')
		if config_backup.exists():
			return
		with config.open('rb') as f:
			data = f.read()
		with config_backup.open('wb') as f:
			f.write(data)
		with config.open('wb') as f:
			f.write(re.sub(rb'(echo[^\n]+OK)', rb': #\1', data))
