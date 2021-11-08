from typing import Iterable, List

from norminette.lexer import Token
from norminette.lexer.dictionary import keywords as _keywords
from norminette.lexer.dictionary import brackets as _brackets
from norminette.lexer.dictionary import operators as _operators

keywords = {v: k for k, v in _keywords.items()}
brackets = {v: k for k, v in _brackets.items()}
operators = {v: k for k, v in _operators.items()}


class TokenStringify:
	def space(self, token: Token) -> str:
		return " "

	def tab(self, token: Token) -> str:
		return "\t"

	def newline(self, token: Token) -> str:
		return "\n"

	def escaped_newline(self, token: Token) -> str:
		return "\\\n"

	def comma(self, token: Token) -> str:
		return ","


class AST:
	tokens: Iterable[Token]

	def __init__(self, tokens: Iterable[Token]) -> None:
		self.tokens = tokens

	def refactor(self) -> 'AST':
		too_many_instr_line = None
		new_tokens: List[Token] = []
		for token in self.tokens:
			if getattr(token, 'to_delete', False):
				continue

			if getattr(token, 'too_many_instr', False):
				token.to_add_newline_before = True
				too_many_instr_line = token.pos[0]

			if getattr(token, 'exp_newline', False):
				token.to_add_newline_before = too_many_instr_line != token.pos[0]

			if getattr(token, 'to_add_newline_before', False):
				self._refactor_add_newline(new_tokens)
			elif getattr(token, 'to_add_space_before', False):
				self._refactor_add_space(new_tokens)

			if hasattr(token, 'indent'):
				self._refactor_indent(token, new_tokens)
			if getattr(token, 'value', None) and token.value[0] == "#":
				self._refactor_preproc(token)
			if token.type == "NEWLINE":
				# delete all spaces before newline
				self._refactor_delete_spaces_before(new_tokens)
			new_tokens.append(token)

			if getattr(token, 'to_add_newline_after', False):
				self._refactor_add_newline(new_tokens)
			elif getattr(token, 'to_add_space_after', False):
				self._refactor_add_space(new_tokens)

		self.tokens = new_tokens
		return self

	def _refactor_add_space(self, new_tokens: List[Token]) -> None:
		# delete all spaces before space
		# we don't use space combined with other spaces
		self._refactor_delete_spaces_before(new_tokens)
		new_tokens.append(Token("SPACE", (-1, -1)))

	def _refactor_add_newline(self, new_tokens: List[Token]) -> None:
		# delete all spaces before newline
		self._refactor_delete_spaces_before(new_tokens)
		new_tokens.append(Token("NEWLINE", (-1, -1)))

	def _refactor_delete_spaces_before(self, new_tokens: List[Token]) -> None:
		while new_tokens and new_tokens[-1].type in ("TAB", "SPACE"):
			del new_tokens[-1]

	def _refactor_indent(self, token: Token, new_tokens: List[Token]) -> None:
		indent = getattr(token, 'indent', 0)
		self._refactor_delete_spaces_before(new_tokens)
		while indent:
			new_tokens.append(Token("TAB", (-1, -1)))
			indent -= 1

	def _refactor_preproc(self, token: Token) -> None:
		value: str = token.value
		i = 1
		if hasattr(token, 'preproc_indent'):
			spaces = " " * token.preproc_indent
			value = f"{value[0]}{spaces}{value[i:].lstrip()}"
		else:
			while value[i] == " ":
				i += 1
			value = f"{value[:i]}{value[i:].lstrip()}"
		token.value = value

	def stringify(self) -> str:
		token_stringifier = TokenStringify()
		content = []
		for token in self.tokens:
			# print(token, token.type, token.value)
			stringify = getattr(token_stringifier, token.type.lower(), None)
			if stringify is not None:
				content.append(stringify(token))
				continue

			for bucket in (keywords, brackets, operators):
				if token.type in bucket:
					content.append(bucket[token.type])
					break
			else:
				if getattr(token, 'value', None):
					content.append(token.value)
					continue
				raise KeyError("Unknown token type for stringify: %s" % token.type)
		return ''.join(content)
