import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

HEADER = """
/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   {filename}[spaces]                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: {login} <{email}>[spaces]                  +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: {created} by {login}[spaces]             #+#    #+#             */
/*   Updated: {updated} by {login}[spaces]            ###    #######.fr       */
/*                                                                            */
/* ************************************************************************** */
"""


class CodeFixer:
	path: Path
	content: Optional[str]
	lines: Optional[List[str]]
	lines_diff: int

	def __init__(self, path: Path):
		self.path = path
		with path.open() as f:
			self.content = f.read()
		self.lines = None
		self.lines_diff = 0

	def get_lines(self) -> List[str]:
		if self.lines is not None:
			return self.lines
		if self.content:
			self.lines = self.content.split("\n")
		else:
			self.lines = []
		self.content = None
		return self.lines

	def get_content(self) -> str:
		if self.content is not None:
			return self.content
		if self.lines:
			self.content = "\n".join(self.lines)
		else:
			self.content = ""
		return self.content

	def set_content(self, content: str) -> None:
		self.content = content
		self.lines = None

	def insert_header(self, username: str, email: str) -> bool:
		if not username:
			raise ValueError("Cannot insert header: username is not provided!")
		if not email:
			raise ValueError("Cannot insert header: email is not provided!")
		stats = self.path.stat()
		dt_format = "%Y/%m/%d %H:%M:%S"
		try:
			created = stats.st_birthtime
		except AttributeError:
			created = int(stats.st_ctime)

		params: Dict[str, str] = {
			"filename": self.path.name,
			"login": username,
			"email": email,
			"created": datetime.fromtimestamp(created).strftime(dt_format),
			"updated": datetime.fromtimestamp(stats.st_mtime).strftime(dt_format),
		}

		def replace_value(match: re.Match) -> str:
			value = params.get(match.group(1).lower())
			if value is not None:
				return value
			return match.group(0)
		spaces_pattern = "[spaces]"
		escaped_spaces_pattern = re.escape("[spaces]")
		header_parts = [x for x in (x.strip() for x in HEADER.split("\n")) if x]
		length = len(header_parts[0])
		new_header_parts = []
		for part in header_parts:
			part = re.sub(r"{(\w+)}", replace_value, part)
			length_diff = length - len(part)
			if length_diff >= 0:
				part = part.replace(spaces_pattern, " " * (len(spaces_pattern) + length_diff))
			else:
				def delete_spaces(match: re.Match) -> str:
					spaces_length = len(match.group(1))
					return " " * (spaces_length + length_diff)
				part = re.sub(rf"({escaped_spaces_pattern}\s*)", delete_spaces, part)
			new_header_parts.append(part)
		new_header_parts.append("")

		header = "\n".join(new_header_parts)
		self.get_lines().insert(0, header)
		self.lines_diff = 1
		return True

	def insert_void_args(self, i: int) -> bool:
		lines = self.get_lines()
		lines[i] = re.sub(r"\([ \t]*", "(void", lines[i])
		return True

	def reformat_function_declaration(self, i: int) -> bool:
		lines = self.get_lines()
		match = re.match(r"^((\s*\w+)+?)\s*(\**)\s*(\w+)\s*\(\s*(.*)$", lines[i])
		if match:
			return_type = " ".join([x.strip() for x in match.group(1).replace("\t", " ").split(" ")])
			asterisk = match.group(3)
			func_name = match.group(4)
			func_other = "(" + match.group(5)
			print(return_type, asterisk, func_name, func_other)
			lines[i] = f"{return_type}\t{asterisk}{func_name}{func_other}"
			return True
		return False

	def fix_multiple_spaces(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		lines[i] = line[:pos] + re.sub(" +", " ", line[pos:], count=1)
		return True

	def fix_multiple_newlines(self, i: int) -> bool:
		lines = self.get_lines()
		deleted_count = 0
		length = len(lines)
		while i < length and not lines[i].strip():
			del lines[i]
			length -= 1
			deleted_count += 1
		self.lines_diff = -deleted_count
		return True

	def fix_space_replace_tab(self, i: int, pos: int) -> bool:
		"""
		Replaces multiple spaces to multiple tabs to keep align about the same
		"""
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		if line[pos - 1] != " ":
			pos += 1
		head = line[:pos]
		space_count = len(head) - len(head.rstrip(' '))
		tab_count = space_count // 4 + int(space_count % 4 != 0)
		tabs = '\t' * tab_count
		lines[i] = f"{line[:pos - space_count]}{tabs}{line[pos:]}"
		return True

	def fix_tab_replace_space(self, i: int, pos: int) -> bool:
		"""
		Replaces multiple tabs to single space. Cause we don't use multiple sapces anywhere
		"""
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		match = re.search(r"\t+", line[pos:])
		if not match:
			return False
		lines[i] = f"{line[:pos + match.start()]} {line[pos + match.end():]}"
		return True

	def fix_brace_should_eol(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos += 1
		pos = self._translate_pos(line, pos)
		lines[i] = f"{line[:pos]}{self.get_new_line()}{line[pos:]}"
		return True

	def fix_brace_newline(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		lines[i] = f"{line[:pos]}{self.get_new_line()}{line[pos:]}"
		return True

	def add_eol(self, i: int) -> bool:
		lines = self.get_lines()
		lines[i] += "\n"
		return True

	def add_space_after_kw(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		match = re.search(r"\w+", line[pos:])
		if not match:
			return False
		start = pos + match.end()
		lines[i] = f"{line[:start]} {line[start:]}"
		return True

	def add_space_after_operator(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		match = re.search(r"[^\"'\w\d(){}\[\]\s\\/]+", line[pos:])
		if not match:
			return False
		start = pos + match.end()
		lines[i] = f"{line[:start]} {line[start:]}"
		return True

	def add_space_after(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		pos += 1
		lines[i] = f"{line[:pos]} {line[pos:]}"
		return True

	def add_space_before(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		lines[i] = f"{line[:pos]} {line[pos:]}"
		return True

	def delete_spaces(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		head = line[:pos]
		space_count = len(head) - len(head.rstrip(' '))
		lines[i] = f"{line[:pos - space_count]}{line[pos:]}"
		return True

	def delete_spaces_after(self, i: int, pos: int) -> bool:
		return self._delete_regexp_after(i, pos, r"[ ]+")

	def delete_whitespaces_after(self, i: int, pos: int) -> bool:
		# for us whitespaces are only tabs ans spaces
		return self._delete_regexp_after(i, pos, r"[\t ]+")

	def _delete_regexp_after(self, i: int, pos: int, regexp: str):
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		match = re.search(regexp, line[pos:])
		if not match:
			return False
		lines[i] = f"{line[:pos + match.start()]}{line[pos + match.end():]}"
		return True

	def fix_too_many_tab(self, i: int, pos: int) -> bool:
		"""
		Aligns line by to fit previous line align level
		"""
		if pos != 0:
			return False
		lines = self.get_lines()
		line = lines[i]
		match = re.search("^\t+", line)
		tabs_count = 0
		if match:
			tabs_count = match.end()
		parent_tabs_count = 0
		if i != 0:
			match = re.search("^\t+", lines[i - 1])
			if match:
				parent_tabs_count = match.end()
		if tabs_count == parent_tabs_count + 1:
			# if inner is still produces error, align to the same level as parent
			target_tabs_count = parent_tabs_count
		else:
			# first try to align as inner structure
			target_tabs_count = parent_tabs_count + 1
		tabs = '\t' * target_tabs_count
		# use lstrip to delete also spaces in case if it's a mixed tab space line
		lines[i] = f"{tabs}{line.lstrip()}"
		return True

	def fix_mixed_space_tab(self, i: int, pos: int):
		"""
		Deletes spaces and preserves only tabs
		If there is only the leading or trailing space, delete tabs
		"""
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		match = re.search("^[\t ]+", line[pos:])
		if not match:
			return False
		pos += match.end()
		head = line[:pos].rstrip()
		whitespaces = line[len(head):pos]
		if " " not in whitespaces[1:]:
			tabs = " "
		else:
			tabs = whitespaces.replace(" ", "")
		lines[i] = f"{head}{tabs}{line[pos:]}"
		return True

	def trim_leading_whitespaces(self, i: int) -> bool:
		"""
		Deletes whitespaces from the beginning of the line
		"""
		lines = self.get_lines()
		lines[i] = lines[i].lstrip()
		return True

	def trim_trailing_whitespaces(self, i: int) -> bool:
		"""
		Deletes whitespaces from the end of the line
		"""
		lines = self.get_lines()
		lines[i] = lines[i].rstrip()
		return True

	def set_preproc_indent(self, i: int, indent: int) -> bool:
		"""
		Sets the given indent to the preprocessor
		"""
		lines = self.get_lines()
		_indent = " " * indent
		lines[i] = f"#{_indent}{lines[i][1:].lstrip()}"
		return True

	def align_by_indent(self, i: int, pos: int, indent: int) -> bool:
		"""
		Aligns line to the given indent by placing tabs at the given pos
		"""
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		while line[pos - 1] != "\t":
			pos -= 1
		head = line[:pos].rstrip()
		space_count = (indent * 4) - self._count_indent_by_line(head)
		tab_count = space_count // 4 + int(space_count % 4 != 0)
		tabs = '\t' * tab_count
		lines[i] = f"{head}{tabs}{line[pos:]}"
		return True

	def add_tab(self, i: int, pos: int):
		"""
		Adds a single tab at `pos`
		"""
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		lines[i] = f"{line[:pos]}\t{line[pos:]}"
		return True

	def wrap_in_braces(self, i_start: int, pos_start: int, i_end: int, pos_end: int) -> bool:
		lines = self.get_lines()
		line = lines[i_start]
		pos = self._translate_pos(line, pos_start)
		lines[i_start] = f"{line[:pos]}({line[pos:]}"

		line = lines[i_end]
		pos = self._translate_pos(line, pos_end)
		if i_start == i_end:
			# +1 because we've added an open brace
			pos += 1
		lines[i_end] = f"{line[:pos]}){line[pos:]}"
		return True

	def _fix_last_line(self) -> bool:
		lines = self.get_lines()
		lines[-1] = lines[-1].strip()
		if lines[-1]:
			lines[-1] += self.get_new_line()
		return True

	def _count_indent_by_line(self, line: str):
		indent = 0
		for ch in line:
			if ch == "\t":
				n = 4 - (indent % 4)
				indent += n
			else:
				indent += 1
		return indent

	def _translate_pos(self, line: str, pos: int) -> int:
		"""
		Norminette counts tabulation as 4 spaces.
		So you can't use your current pos for determining position of error in a line.
		"""
		i = 0
		j = 0
		while i < pos:
			if line[i] == "\t":
				n = 4 - (j % 4)
				pos -= n - 1
				j += n
			else:
				j += 1
			i += 1
		if pos < 0:
			return 0
		return pos

	def get_new_line(self) -> str:
		lines = self.get_lines()
		return "\r\n" if lines[0] and lines[0][-1] == "\r" else "\n"

	def save(self, path: Optional[Path] = None) -> None:
		path = path or self.path
		self._fix_last_line()
		with path.open("w") as f:
			f.write(self.get_content())
