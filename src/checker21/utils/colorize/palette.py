from __future__ import annotations
from typing import TypeVar, Type, Callable, Dict, Union

from .style import Style, NO_STYLE

NO_COLOR_PALETTE = 'nocolor'
COLORED_PALETTE = 'colored'
DEFAULT_PALETTE = COLORED_PALETTE
PALETTES: Dict[str, Type[Palette]] = {}


def register_palette(name: str) -> Callable[[Type[Palette]], Type[Palette]]:
	def _register_palette(palette: Type[Palette]) -> Type[Palette]:
		global PALETTES

		PALETTES[name] = palette
		return palette
	return _register_palette


_P = TypeVar('_P', bound='Palette')


@register_palette(NO_COLOR_PALETTE)
class Palette:
	ERROR: Style   = NO_STYLE
	SUCCESS: Style = NO_STYLE
	WARNING: Style = NO_STYLE
	NOTICE: Style  = NO_STYLE
	INFO: Style    = NO_STYLE

	def update(self: _P, palette: Union[_P, Type[_P]]) -> None:
		self.__dict__.update(palette.__dict__)

	@classmethod
	def create_new(cls: Type[_P]) -> _P:
		return cls()


@register_palette(COLORED_PALETTE)
class ColoredPalette(Palette):
	ERROR   = Style('red',      opts = ('bold',))
	SUCCESS = Style('green',    opts = ('bold',))
	WARNING = Style('yellow',   opts = ('bold',))
	NOTICE  = Style('red')
	INFO    = Style('blue')
