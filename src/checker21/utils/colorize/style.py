from typing import Optional, Tuple

from .color import colorize


class Style:
	__slots__ = ('fg', 'bg', 'opts', 'noreset')
	fg: Optional[str]
	bg: Optional[str]
	opts: Optional[Tuple[str, ...]]
	noreset: bool

	def __init__(
			self,
			fg: Optional[str] = None,
			bg: Optional[str] = None,
			*,
			opts: Optional[Tuple[str, ...]] = None,
			noreset: bool = False
	) -> None:
		self.fg = fg
		self.bg = bg
		self.opts = opts
		self.noreset = noreset

	def __call__(self, text: str) -> str:
		return colorize(text, fg=self.fg, bg=self.bg, opts=self.opts, noreset=self.noreset)

	def __str__(self) -> str:
		return f"Style {self.fg}/{self.bg} [{','.join(self.opts or ())}]"


class NoStyle(Style):
	def __init__(self) -> None:
		super().__init__(None, None, opts=None)

	def __call__(self, text: str) -> str:
		return text

	def __str__(self) -> str:
		return f"NoStyle"


NO_STYLE = NoStyle()
