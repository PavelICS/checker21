import re

from checker21.core import GitChecker
from checker21.utils.bash import bash
from checker21.utils.files import update_file_with_backup


class PftChecker(GitChecker):
	name = 'pft'
	verbose_name = 'PFT'
	description = 'Downloads PFT checker and runs it'

	git_url = 'https://github.com/gavinfielder/pft'
	target_dir = 'pft'

	def run(self, project, subject):
		self.git_config(subject)
		bash(['./reset-to-default-enabled-tests'], capture_output=False)
		if subject.bonus:
			bash(['./disable-test'], capture_output=False)
			bash(['./enable-test', 'bonus'], capture_output=False)
		bash(['./disable-test', 'notintsubject'])
		bash(['./disable-test', '"*_e_"'])
		bash(['./disable-test', '"*_a_"'])
		bash(['./disable-test', '"*_f_"'])
		bash(['./disable-test', '"*_g_"'])
		bash(['./disable-test', '"*_G_"'])
		bash(['./disable-test', '"*_n_"'])
		bash(['./disable-test', '"*_o_"'])
		bash(['./disable-test', '"*_D_"'])
		bash(['./disable-test', '"bonus_mix"'])
		bash(['./disable-test', '"*swap"'])
		bash(['./disable-test', '"*argnum"'])
		bash(['make'], capture_output=False)
		bash(['./test'], capture_output=False)

	def git_config(self, subject):
		def callback(data):
			makefile_count = sum([1 for file in subject.list_files() if file.endswith("Makefile")])
			if makefile_count > 1:
				# Activate separate libft
				data = data.replace(b'USE_SEPARATE_LIBFT=0', b'USE_SEPARATE_LIBFT=1')
			# Change path to source files
			data = data.replace(b'../libft', b'../../libft')
			data = data.replace(b'LIBFTPRINTF_DIR=..', b'LIBFTPRINTF_DIR=../..')
			# Disable auto remake
			data = data.replace(b'ENABLE_DISABLE_REMAKES_PFT=1', b'ENABLE_DISABLE_REMAKES_PFT=0')
			return data

		update_file_with_backup('options-config.ini', callback)
