from .style import Style, NO_STYLE

NO_COLOR_PALETTE = 'nocolor'
COLORED_PALETTE = 'colored'
DEFAULT_PALETTE = COLORED_PALETTE
PALETTES = {}

def register_palette(name):
	def _register_palette(palette):
		global PALETTES

		PALETTES[name] = palette
		return palette
	return _register_palette


@register_palette(NO_COLOR_PALETTE)
class Palette:
	ERROR   = NO_STYLE
	SUCCESS = NO_STYLE
	WARNING = NO_STYLE
	NOTICE  = NO_STYLE
	INFO    = NO_STYLE

	def update(self, palette):
		self.__dict__.update(palette.__dict__)

	@classmethod
	def create_new(cls):
		return cls()


@register_palette(COLORED_PALETTE)
class ColoredPalette(Palette):
	ERROR   = Style('red',      opts = ('bold',))
	SUCCESS = Style('green',    opts = ('bold',))
	WARNING = Style('yellow',   opts = ('bold',))
	NOTICE  = Style('red')
	INFO    = Style('blue')
