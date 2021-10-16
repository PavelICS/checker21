import re
from pathlib import Path
from datetime import datetime
from typing import Dict

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

	def __init__(self, path: Path):
		self.path = path
		with path.open() as f:
			self.content = f.read()

	def insert_header(self, login: str, email: str) -> None:
		stats = self.path.stat()
		dt_format = "%Y/%m/%d %H:%M:%S"
		try:
			created = stats.st_birthtime
		except AttributeError:
			created = stats.st_ctime

		params: Dict[str, str] = {
			"filename": self.path.name,
			"login": login,
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
		header_parts = (x.strip() for x in HEADER.split("\n"))
		header_parts = [x for x in header_parts if x]
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
		self.content = header + self.content.lstrip()

	def delete_file_leading_spaces(self) -> None:
		self.content = self.content.lstrip()

	def save(self) -> None:
		with self.path.open("w") as f:
			f.write(self.content)
