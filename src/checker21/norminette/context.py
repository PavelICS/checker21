from typing import Tuple, List, Dict

from norminette.context import Context as NorminetteContext
from norminette.lexer import Token
from norminette.norm_error import NormError
from norminette.scope import Scope

from .fix_machine import NorminetteFixMachine


class Context(NorminetteContext):
	fix_machine: NorminetteFixMachine
	func_decl_align: List[Tuple[Token, int]]
	var_decl_align: Dict[Scope, List[Tuple[Token, int]]]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.func_decl_align = []
		self.var_decl_align = {}

	def set_fix_machine(self, fix_machine: NorminetteFixMachine) -> None:
		self.fix_machine = fix_machine

	def fix_error(self, errno: str, tkn_pos: int, **kwargs) -> None:
		token: Token = self.peek_token(tkn_pos)
		error = NormError(errno, token.pos[0], token.pos[1])
		if 'end' in kwargs:
			end_token: Token = self.peek_token(kwargs['end'])
			kwargs['end_line'] = end_token.pos[0] - 1
			kwargs['end_col'] = end_token.pos[1] - 1
		# TODO move full logic to checker21 NorminetteError + fix_norm_error
		func_name = f"fix_{errno.lower()}"
		func = getattr(self.fix_machine, func_name, None)
		if func is not None:
			kwargs['line'] = token.pos[0] - 1
			kwargs['col'] = token.pos[1] - 1
			self.fix_machine.on_fix_processor_found(str(error))
			if func(**kwargs):
				self.fix_machine.fix_count += 1
		else:
			self.fix_machine.on_fix_processor_not_found(errno)

	def add_func_decl_align(self, tkn: Token, indent: int) -> None:
		self.func_decl_align.append((tkn, indent))

	def add_var_decl_align(self, tkn: Token):
		scope: Scope = self.scope
		if scope not in self.var_decl_align:
			self.var_decl_align[scope] = []
		self.var_decl_align[scope].append((tkn, tkn.pos[1]))
