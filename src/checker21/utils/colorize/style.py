
from .color import colorize


class Style:
	__slots__ = ('fg', 'bg', 'opts', 'noreset')

	def __init__(self, fg=None, bg=None, *, opts=None, noreset=False):
		self.fg = fg
		self.bg = bg
		self.opts = opts
		self.noreset = noreset

	def __call__(self, text):
		return colorize(text, fg=self.fg, bg=self.bg, opts=self.opts, noreset=self.noreset)

	def __str__(self):
		return f"Style {self.fg}/{self.bg} [{','.join(self.opts or ())}]"


class NoStyle(Style):
	def __init__(self):
		super().__init__(None, None, opts=None)

	def __call__(self, text):
		return text

	def __str__(self):
		return f"NoStyle"


NO_STYLE = NoStyle()
