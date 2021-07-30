import re

from checker21.core import GitChecker
from checker21.utils.bash import bash
from checker21.utils.files import update_file_with_backup


class LibftUnitTestChecker(GitChecker):
	name = 'libft-unit-test'
	verbose_name = 'Libft-unit-test'
	description = 'Downloads libft-unit-test checker and runs it'

	git_url = 'https://github.com/alelievr/libft-unit-test'
	target_dir = 'libft-unit-test'

	def run(self, project, subject):
		self.git_config()
		bash(['make', 'f'], capture_output=False)

	def git_config(self):
		def callback(data):
			# Change path to source files
			data = data.replace(b'../libft\n', b'../..\n')
			return data

		update_file_with_backup('Makefile', callback)
