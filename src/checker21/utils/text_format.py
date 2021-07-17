
def align_line(line, width, fill=' '):
	length = len(line)
	if length >= width:
		return line
	count = width - length
	padding_left = fill * (count // 2)
	padding_right = fill * ((count + 1) // 2)
	return f'{padding_left}{line}{padding_right}'

