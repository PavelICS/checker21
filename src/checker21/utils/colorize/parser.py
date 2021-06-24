from .color import color_names, opt_dict
from .palette import  PALETTES, NO_COLOR_PALETTE, DEFAULT_PALETTE
from .style import Style

def parse_color_setting(config_string):
	"""Parse a config_string to produce the system palette
	The general form of a palette definition is:
		"palette;role=fg;role=fg/bg;role=fg,option,option;role=fg/bg,option,option"
	where:
		palette is a named palette; one of 'colored', or 'nocolor'.
		role is a named style used by Checker21
		fg is a foreground color.
		bg is a background color.
		option is a display options.
	Specifying a named palette is the same as manually specifying the individual
	definitions for each role. Any individual definitions following the palette
	definition will augment the base palette definition.
	Valid roles:
		'error', 'success', 'warning', 'notice', 'info'
	Valid colors:
		'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'
	Valid options:
		'bold', 'underscore', 'blink', 'reverse', 'conceal', 'noreset'
	"""
	if not config_string:
		return PALETTES[DEFAULT_PALETTE]

	no_color_palette = PALETTES[NO_COLOR_PALETTE]

	# Split the color configuration into parts
	parts = config_string.lower().split(';')
	palette = no_color_palette.create_new()
	changed_styles = 0
	for part in parts:
		if part in PALETTES:
			# A default palette has been specified
			palette.update(PALETTES[part])
		elif '=' in part:
			# Break the definition into the role,
			# plus the list of specific instructions.
			# The role must be in upper case
			role, instructions = part.split('=')
			role = role.upper()

			# The nocolor palette has all available roles.
			# Use that palette as the basis for determining
			# if the role is valid.
			if not hasattr(no_color_palette, role):
				continue

			# Process a palette defining string
			definition = {}

			styles = instructions.split(',')
			styles.reverse()

			# The first instruction can contain a slash
			# to break apart fg/bg.
			colors = styles.pop().split('/')
			if colors:
				if colors[0] in color_names:
					definition['fg'] = colors[0]
				if len(colors) > 1 and colors[1] in color_names:
					definition['bg'] = colors[1]

			# All remaining instructions are options
			if 'noreset' in styles:
				definition['noreset'] = True
			definition['opts'] = tuple(s for s in styles if s in opt_dict) or None


			if definition:
				changed_styles += 1
				setattr(palette, role, Style(**definition))

	# If there are no colors specified, return the empty palette.
	if changed_styles == 0:
		return None
	return palette

