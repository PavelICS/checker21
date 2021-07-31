import checker21
from checker21.management.base import BaseCommand


class Command(BaseCommand):
	help = f'Displays current Checker21 version ({checker21.__version__}).'

	def handle(self, *args, **options):
		self.stdout.write(checker21.__version__)
