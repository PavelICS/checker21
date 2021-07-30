from typing import Optional, Tuple

color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
foreground = {color_names[x]: f'3{x}' for x in range(8)}
background = {color_names[x]: f'4{x}' for x in range(8)}

RESET = '0'
opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}


def colorize(
		text: str = '',
		fg: Optional[str] = None,
		bg: Optional[str] = None,
		opts: Optional[Tuple[str, ...]] = None,
		noreset: bool = False
) -> str:
	"""
		Return your text, enclosed in ANSI graphics codes.
		Return the RESET code if no parameters are given.
		Valid colors:
			'black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white'
		Valid options:
			'bold'
			'underscore'
			'blink'
			'reverse'
			'conceal'
		Extra options:
			noreset - string will not be auto-terminated with the RESET code
		Examples:
			colorize('hello', fg='red', bg='blue', opts=('blink',))
			colorize()
			colorize('goodbye', opts=('underscore',))
			print(colorize('first line', fg='red', noreset=True)))
			print('this should be red too')
			print(colorize('and so should this'))
			print('this should not be red')
	"""
	if opts:
		code_list = [opt_dict[o] for o in opts if o in opt_dict]
	else:
		code_list = []
	if fg:
		code_list.append(foreground[fg])
	if bg:
		code_list.append(background[bg])

	if not noreset:
		text = f"{text}\x1b[{RESET}m"
	if code_list:
		codes = ';'.join(code_list)
		text = f"\x1b[{codes}m{text}"
	return text
