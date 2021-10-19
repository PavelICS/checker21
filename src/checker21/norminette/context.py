from typing import Tuple, List

from norminette.context import Context as NorminetteContext
from norminette.lexer import Token
from norminette.norm_error import NormError

from .fix_machine import NorminetteFixMachine


class Context(NorminetteContext):
	fix_machine: NorminetteFixMachine
	func_decl_align: List[Tuple[Token, int]]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.func_decl_align = []

	def set_fix_machine(self, fix_machine: NorminetteFixMachine) -> None:
		self.fix_machine = fix_machine

	def fix_error(self, errno: str, tkn: Token, **kwargs) -> None:
		error = NormError(errno, tkn.pos[0], tkn.pos[1])
		# TODO move full logic to checker21 NorminetteError + fix_norm_error
		func_name = f"fix_{errno.lower()}"
		func = getattr(self.fix_machine, func_name, None)
		if func is not None:
			kwargs['line'] = tkn.pos[0] - 1
			kwargs['col'] = tkn.pos[1]
			self.fix_machine.on_fix_processor_found(str(error))
			if func(**kwargs):
				self.fix_machine.fix_count += 1
		else:
			self.fix_machine.on_fix_processor_not_found(errno)

	def add_func_decl_align(self, tkn: Token, indent: int) -> None:
		self.func_decl_align.append((tkn, indent))
