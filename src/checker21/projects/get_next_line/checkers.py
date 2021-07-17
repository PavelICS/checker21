import os
import re
from pathlib import Path

from checker21.core import GitChecker
from checker21.utils.bash import bash
from checker21.utils.files import update_file_with_backup


class GnlWarMachineChecker(GitChecker):
	name = 'gnl-war-machine'
	verbose_name = 'GNL war machine'
	description = 'Downloads gnl-war-machine-v2021 checker and runs it'

	git_url = 'https://github.com/PavelICS/gnl-war-machine-v2019'
	target_dir = 'gnl-war-machine-v2021'

	def run(self, subject):
		os.chdir(self.target_dir)
		self.git_config()
		bash(['/bin/bash', 'grademe.sh'], stdout=self.stdout, stderr=self.stderr)
		os.chdir('..')

	def git_config(self):
		def callback(data):
			# change path in config to source files
			return data.replace(b'../../get_next_line', b'../')
		update_file_with_backup('my_config.sh', callback)


# It's a checker for an old subject.
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
		# copy source files
		bash(['cp', '../get_next_line.h', '.'])
		bash(['cp', '../get_next_line.c', '.'])
		bash(['cp', '../get_next_line_utils.c', '.'])

		def callback(data):
			# clear too much output
			return re.sub(rb'(echo[^\n]+OK)', rb': #\1', data)
		update_file_with_backup('run.sh', callback)
