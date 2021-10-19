from checker21.core import Checker

__all__ = ('NorminetteChecker',)


class NorminetteChecker(Checker):
	name = 'norminette'
	verbose_name = 'Norminette'
	description = 'Runs installed norminette to check for files matching Norm'

	def run(self, project, subject):
		from checker21.management.commands.norminette import Command
		cmd = Command(stdout=self.stdout, stderr=self.stderr)
		cmd.set_style(self.style)
		cmd._norminette = cmd.load_norminette(project)
		cmd.handle_check(project)
