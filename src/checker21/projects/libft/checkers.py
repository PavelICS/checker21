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


class LibftSplitChecker(GitChecker):
	name = 'split'
	verbose_name = 'Libft split'
	description = 'Checks split function'

	git_url = "https://github.com/Ysoroko/FT_SPLIT_TESTER"
	target_dir = "libft-split-checker"

	def run(self, project, subject):
		self.git_config()
		bash(["make"], capture_output=False)
		self.stdout.write(self.style.WARNING(
			"The 18 and 19 tests are testing for NULL string as input.\n"
			"We think that it isn't required to check for NULL and segfault here is OK."
		))

	def git_config(self):
		def update_file(data):
			data = data.replace(b"../*.c", b"../../*.c")
			return data

		update_file_with_backup("Makefile", update_file)


class LibftTesterChecker(GitChecker):
	name = 'libft-tester'
	verbose_name = 'LibftTester'
	description = 'Downloads LibftTester checker and runs it'

	git_url = "https://github.com/Tripouille/libftTester"
	target_dir = "libft-tester"

	def run(self, project, subject):
		self.git_config()
		bash(["make", "a"], capture_output=False)

	def git_config(self):
		def update_file(data):
			data = data.replace(b"= $(PARENT_DIR)", b"= ../../")
			return data

		update_file_with_backup("Makefile", update_file)
