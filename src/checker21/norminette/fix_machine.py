from pathlib import Path
from typing import Optional, Any

from checker21.utils.code_fixer import CodeFixer
from checker21.utils.norminette import NorminetteError


class NorminetteFixMachine:
	code_fixer: CodeFixer
	current_line: int
	fix_count: int
	context: Any

	def __init__(self, stdout, stderr, style):
		self.stdout = stdout
		self.stderr = stderr
		self.style = style

	def load_file(self, path: Path) -> None:
		self.code_fixer = CodeFixer(path)
		self.current_line = 0
		self.fix_count = 0
		self.context = None

	def save(self, path: Optional[Path] = None) -> None:
		self.code_fixer.save(path=path)

	def set_code_fixer(self, code_fixer: CodeFixer) -> None:
		self.code_fixer = code_fixer

	def fix_norm_error(self, error: NorminetteError) -> bool:
		if self.current_line >= error.line:
			# do not fix multiple errors on the same line
			return False
		self.current_line = error.line

		kwargs = {
			"line": error.line - 1,
			"col": error.col - 1,
		}
		func_name = f"fix_{error.code.lower()}"
		func = getattr(self, func_name, None)
		if func is not None:
			self.on_fix_processor_found(str(error))
			if func(**kwargs):
				self.fix_count += 1
				return True
		else:
			self.on_fix_processor_not_found(error.code)
		return False

	def on_fix_processor_found(self, error: str) -> None:
		self.stdout.write(f"Fixing {error}")

	def on_fix_processor_not_found(self, errno: str) -> None:
		self.stderr.write(f"No fix processor for {errno}")

	def fix_preproc_start_line(self, line: int, **kwargs) -> bool:
		return self.code_fixer.trim_leading_whitespaces(line)

	def fix_preproc_bad_indent(self, line: int, indent: int, **kwargs) -> bool:
		return self.code_fixer.set_preproc_indent(line, indent)

	def fix_too_many_tab(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.fix_too_many_tab(line, col)

	def get_func_alignment_indent(self) -> int:
		if self.context is None:
			return 0
		return self.context.scope.func_alignment

	def fix_misaligned_func_decl(self, **kwargs) -> bool:
		"""
		Works only after `run_with_norminette` execution
		"""
		indent = self.get_func_alignment_indent()
		if indent == 0:
			return False
		for tkn, func_indent in self.context.func_decl_align:
			if func_indent == indent:
				continue
			print(self.context.filename, tkn, tkn.pos, func_indent)
			line = tkn.pos[0] - 1
			col = tkn.pos[1] - 1
			self.code_fixer.align_by_indent(line, col, indent)
		self.context.func_decl_align = []
		return True

	def run_with_norminette(self) -> bool:
		from norminette.lexer import Lexer
		from checker21.norminette.context import Context
		from checker21.norminette.registry import registry

		source = self.code_fixer.get_content()
		try:
			lexer = Lexer(source)
			tokens = lexer.get_tokens()
		except KeyError:
			# print("Error while parsing file:", e)
			return False
		context = Context(self.code_fixer.path.name, tokens)
		context.set_fix_machine(self)
		registry.run(context, source)
		self.context = context
		return True
