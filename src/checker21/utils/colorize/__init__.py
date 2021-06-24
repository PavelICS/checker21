"""
Sets up the terminal color scheme.
"""

import os
import sys
from .palette import NO_COLOR_PALETTE, PALETTES
from .parser import parse_color_setting

try:
	import colorama
	colorama.init()
except (ImportError, OSError):
	HAS_COLORAMA = False
else:
	HAS_COLORAMA = True

def supports_color():
	"""
	Return True if the running system's terminal supports color,
	and False otherwise.
	"""
	def vt_codes_enabled_in_windows_registry():
		"""
		Check the Windows Registry to see if VT code handling has been enabled
		by default, see https://superuser.com/a/1300251/447564.
		"""
		try:
			# winreg is only available on Windows.
			import winreg
		except ImportError:
			return False
		else:
			reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Console')
			try:
				reg_key_value, _ = winreg.QueryValueEx(reg_key, 'VirtualTerminalLevel')
			except FileNotFoundError:
				return False
			else:
				return reg_key_value == 1

	# isatty is not always implemented, #6223.
	is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

	return is_a_tty and (
		sys.platform != 'win32' or
		HAS_COLORAMA or
		'ANSICON' in os.environ or
		# Windows Terminal supports VT codes.
		'WT_SESSION' in os.environ or
		# Microsoft Visual Studio Code's built-in terminal supports colors.
		os.environ.get('TERM_PROGRAM') == 'vscode' or
		vt_codes_enabled_in_windows_registry()
	)

def get_color_style(colors='', force_color=False):
	"""
	Return a Style object from the color scheme.
	"""
	if not force_color and not supports_color():
		return PALETTES[NO_COLOR_PALETTE]
	return parse_color_setting(colors)
