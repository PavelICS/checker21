
__all__ = ('Checker',)


class Checker:

	name = None
	verbose_name = None
	description = None

	def run(self, subject):
		pass

	def __call__(self, subject):
		self.run(subject)

	def __str__(self):
		return str(self.verbose_name or self.name)

	def __repr__(self):
		return f"{self.__class__}[{self}]"

