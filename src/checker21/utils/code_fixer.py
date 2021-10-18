import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List, Tuple

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
	fix_count: int

	def __init__(self, path: Path):
		self.path = path
		with path.open() as f:
			self.content = f.read()
		self.lines = None
		self.fix_count = 0

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
		new_header_parts.append("\n")

		header = "\n".join(new_header_parts)
		self.content = header + self.get_content().lstrip()
		self.fix_count += 1
		return True

	def delete_file_leading_spaces(self) -> bool:
		self.content = self.get_content().lstrip()
		self.fix_count += 1
		return True

	def insert_void_args(self, i: int) -> bool:
		lines = self.get_lines()
		lines[i] = re.sub(r"\([ \t]*", "(void", lines[i])
		self.fix_count += 1
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
			self.fix_count += 1
			return True
		return False

	def fix_multiple_spaces(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		lines[i] = line[:pos] + re.sub(" +", " ", line[pos:], count=1)
		self.fix_count += 1
		return True

	def fix_multiple_newlines(self, i: int) -> bool:
		lines = self.get_lines()
		length = len(lines)
		while i < length and not lines[i].strip():
			del lines[i]
			length -= 1
		self.fix_count += 1
		return True

	def fix_space_replace_tab(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		if line[pos - 1] != " ":
			pos += 1
		print("real pos", pos)
		head = line[:pos]
		print(head.encode())
		space_count = len(head) - len(head.rstrip(' '))
		tab_count = space_count // 4 + int(space_count % 4 != 0)
		print(space_count, tab_count)
		tabs = '\t' * tab_count
		lines[i] = f"{line[:pos - space_count]}{tabs}{line[pos:]}"
		self.fix_count += 1
		return True

	def fix_brace_should_eol(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos += 1
		pos = self._translate_pos(line, pos)
		lines[i] = f"{line[:pos]}{self.get_new_line()}{line[pos:]}"
		self.fix_count += 1
		return True

	def add_space_after_kw(self, i: int, pos: int) -> bool:
		lines = self.get_lines()
		line = lines[i]
		pos = self._translate_pos(line, pos)
		print(line[pos:])
		match = re.search(r"\w+", line[pos:])
		if not match:
			return False
		start = pos + match.end()
		lines[i] = f"{line[:start]} {line[start:]}"
		self.fix_count += 1
		return True

	def _fix_last_line(self) -> bool:
		lines = self.get_lines()
		lines[-1] = lines[-1].strip()
		if lines[-1]:
			lines[-1] += self.get_new_line()
		return True

	def _translate_pos(self, line: str, pos: int) -> int:
		"""
		Norminette counts tabulation as 4 spaces.
		So you can't use your current pos for determining position of error in a line.
		"""
		i = 0
		while i < pos:
			if line[i] == "\t":
				pos -= 3
			i += 1
		return pos

	def get_new_line(self) -> str:
		lines = self.get_lines()
		return "\r\n" if lines[0] and lines[0][-1] == "\r" else "\n"

	def save(self) -> None:
		with self.path.open("w") as f:
			self._fix_last_line()
			f.write(self.get_content())
