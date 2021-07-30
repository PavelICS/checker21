import re

from checker21.core import GitChecker
from checker21.utils.bash import bash
from checker21.utils.files import update_file_with_backup


class GnlWarMachineChecker(GitChecker):
	name = 'gnl-war-machine'
	verbose_name = 'GNL War Machine'
	description = 'Downloads gnl-war-machine-v2021 checker and runs it'

	git_url = 'https://github.com/PavelICS/gnl-war-machine-v2019'
	target_dir = 'gnl-war-machine-v2021'

	def run(self, project, subject):
		self.git_config()
		cmd = bash(['/bin/bash', 'grademe.sh'], capture_output=False)

	def git_config(self):
		def callback(data):
			# Change path to source files
			data = data.replace(b'../../get_next_line', b'../../')
			# Turn off norminette checker. We have our own norminette check
			data = data.replace(b'NORM=1', b'NORM=0')
			return data
		update_file_with_backup('my_config.sh', callback)


class GnlTesterChecker(GitChecker):
	name = 'gnltester'
	verbose_name = 'GNL Tester'
	description = 'Downloads gnlTester checker and runs it'

	git_url = 'https://github.com/Tripouille/gnlTester'
	target_dir = 'gnltester'

	def run(self, project, subject):
		self.git_config()
		if subject.bonus:
			cmd = bash(['make', 'b'], capture_output=False)
		else:
			cmd = bash(['make', 'm'], capture_output=False)

	def git_config(self):
		def callback(data):
			# Change path to source files
			data = data.replace(b'../get_next_line', b'../../get_next_line')
			data = data.replace(b'../%.c=%.o', b'../../%.c=%.o')
			data = data.replace(b'-I..', b'-I../..')
			data = data.replace(b'../*bonus.c', b'../../*bonus.c')
			return data
		update_file_with_backup('Makefile', callback)


# It's a checker for an old subject.
class GnlKillerChecker(GitChecker):
	name = 'gnlkiller'
	verbose_name = 'GNL Killer'
	description = 'Downloads gnlkiller checker and runs it'

	git_url = 'https://github.com/DontBreakAlex/gnlkiller'
	target_dir = 'gnlkiller'

	def run(self, project, subject):
		self.git_config()
		bash(['/bin/bash', 'run.sh'], stdout=self.stdout, stderr=self.stderr)

	def git_config(self):
		# copy source files
		bash(['cp', '../../get_next_line.h', '.'])
		bash(['cp', '../../get_next_line.c', '.'])
		bash(['cp', '../../get_next_line_utils.c', '.'])

		def callback(data):
			# clear too much output
			return re.sub(rb'(echo[^\n]+OK)', rb': #\1', data)
		update_file_with_backup('run.sh', callback)
