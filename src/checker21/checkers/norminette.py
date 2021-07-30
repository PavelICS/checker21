from checker21.core import Checker
from checker21.utils.norminette import get_norminette_version, NorminetteCheckStatus, run_norminette

__all__ = ('NorminetteChecker',)


class NorminetteChecker(Checker):
	name = 'norminette'
	verbose_name = 'Norminette'
	description = 'Runs installed norminette to check for files matching Norm'

	def run(self, project, subject):
		version = get_norminette_version()
		if version is None:
			self.stdout.write(self.style.ERROR("Norminette is not found!"))
			return
		self.stdout.write(self.style.INFO(f"Using norminette {version}"))

		files = [file for file in subject.list_files() if file.endswith(".c") or file.endswith(".h")]
		result = run_norminette(files)
		for file, info in result.items():
			status = info["status"]

			if status == NorminetteCheckStatus.OK:
				self.stdout.write(self.style.SUCCESS(info["line"]))

			elif status == NorminetteCheckStatus.NOT_VALID:
				self.stdout.write(self.style.WARNING(info["line"]))

			elif status == NorminetteCheckStatus.ERROR:
				self.stdout.write(self.style.ERROR(info["line"]))
				for error in info["errors"]:
					self.stdout.write(error)

			if "warnings" in info:
				for warning in info["warnings"]:
					self.stdout.write(self.style.WARNING(warning))
