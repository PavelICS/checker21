from pathlib import Path
from typing import Optional, Any

from checker21.norminette.ast import AST
from checker21.utils.code_fixer import CodeFixer
from checker21.utils.norminette import NorminetteError


class NorminetteFixMachine:
	code_fixer: CodeFixer
	current_line: int  # The last line where the errors was fixed
	base_line: int  # The last position where code still is not deleted
	fix_count: int  # how many errors were fixed
	context: Any
	line_shift: int
	has_empty_line_first: bool
	user: str
	email: str

	def __init__(self, stdout, stderr, style):
		self.stdout = stdout
		self.stderr = stderr
		self.style = style

	def load_file(self, path: Path) -> None:
		self.code_fixer = CodeFixer(path)
		self.current_line = 0
		self.base_line = 0
		self.line_shift = 0
		self.has_empty_line_first = False
		self.context = None
		self.fix_count = 0

	def set_user_email(self, user: str, email: str) -> None:
		self.user = user
		self.email = email

	def save(self, path: Optional[Path] = None) -> None:
		self.code_fixer.save(path=path)

	def set_code_fixer(self, code_fixer: CodeFixer) -> None:
		self.code_fixer = code_fixer

	def fix_norm_error(self, error: NorminetteError) -> bool:
		if self.base_line >= error.line:
			self.on_fix_processor_found(str(error))
			self.fix_count += 1
			return True

		if self.current_line >= error.line:
			# do not fix multiple errors on the same line
			return False
		self.current_line = error.line

		kwargs = {
			"line": error.line - 1 + self.line_shift,
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
			line = tkn.pos[0] - 1
			col = tkn.pos[1] - 1
			self.code_fixer.align_by_indent(line, col, indent)
		self.context.func_decl_align = []
		return True

	def get_closest_func_scope(self, line: int) -> Optional[Any]:
		if self.context is None:
			return None
		for func_scope, vars_list in self.context.var_decl_align.items():
			for tkn, indent in vars_list:
				if (tkn.pos[0] - 1) == line:
					return func_scope

	def fix_misaligned_var_decl(self, line: int, **kwargs) -> bool:
		"""
		Works only after `run_with_norminette` execution
		"""
		func_scope = self.get_closest_func_scope(line)
		if func_scope is None:
			return False

		if getattr(func_scope, 'is_misaligned_var_decl_fixed', False):
			return True

		indent = func_scope.vars_alignment
		for tkn, var_indent in self.context.var_decl_align[func_scope]:
			if var_indent == indent:
				continue
			line = tkn.pos[0] - 1
			col = tkn.pos[1] - 1
			self.code_fixer.align_by_indent(line, col, indent // 4)
		func_scope.is_misaligned_var_decl_fixed = True
		return True

	def fix_return_parenthesis(self, line: int, col: int, end_line: int, end_col: int, **kwargs) -> bool:
		self.current_line = end_line  # change the last line to the end_line
		return self.code_fixer.wrap_in_braces(line, col, end_line, end_col)

	def fix_no_args_void(self, line: int, **kwargs) -> bool:
		return self.code_fixer.insert_void_args(line)

	def fix_space_before_func(self, line: int, **kwargs) -> bool:
		return self.code_fixer.reformat_function_declaration(line)

	def fix_consecutive_spc(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.fix_multiple_spaces(line, col)

	def fix_space_replace_tab(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.fix_space_replace_tab(line, col)

	def fix_space_after_kw(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.add_space_after_kw(line, col)

	def fix_spc_after_par(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.add_space_after(line, col)

	def fix_spc_after_operator(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.add_space_after_operator(line, col)

	def fix_spc_bfr_operator(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.add_space_before(line, col)

	def fix_no_spc_bfr_opr(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.delete_spaces(line, col)

	def fix_no_spc_afr_par(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.delete_spaces_after(line, col)

	def fix_tab_instead_spc(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.fix_tab_replace_space(line, col)

	def fix_tab_replace_space(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.fix_tab_replace_space(line, col)

	def fix_too_many_tab(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.fix_too_many_tab(line, col)

	def fix_too_few_tab(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.add_tab(line, col)

	def fix_mixed_space_tab(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.fix_mixed_space_tab(line, col)

	def fix_nl_after_var_decl(self, line: int, **kwargs) -> bool:
		self.current_line = line - 1
		return self.code_fixer.add_eol(line - 1)

	def fix_spc_after_pointer(self, line: int, col: int, **kwargs) -> bool:
		return self.code_fixer.delete_whitespaces_after(line, col)

	def fix_spc_before_nl(self, line: int, **kwargs) -> bool:
		return self.code_fixer.trim_trailing_whitespaces(line)

	def fix_brace_newline(self, line: int, col: int, **kwargs) -> bool:
		# it inserts a new line inside current line, so we can continue fixing errors
		return self.code_fixer.fix_brace_newline(line, col)

	def fix_brace_should_eol(self, line: int, col: int, **kwargs) -> bool:
		# it inserts a new line inside current line, so we can continue fixing errors
		return self.code_fixer.fix_brace_should_eol(line, col)

	def fix_consecutive_newlines(self, line: int, **kwargs) -> bool:
		if self.code_fixer.fix_multiple_newlines(line):
			self.line_shift += self.code_fixer.lines_diff
			self.base_line = self.current_line - (self.code_fixer.lines_diff + 1)
			return True
		return False

	def fix_empty_line_file_start(self, **kwargs) -> bool:
		return self.fix_consecutive_newlines(0)

	def fix_empty_line_function(self, line: int, **kwargs) -> bool:
		return self.fix_consecutive_newlines(line)

	def fix_invalid_header(self, **kwargs) -> bool:
		if self.has_empty_line_first:
			return False
		if self.code_fixer.insert_header(self.user, self.email):
			self.line_shift += self.code_fixer.lines_diff
			return True
		return False

	def _init_norminette_context(self):
		from norminette.lexer import Lexer
		from checker21.norminette.context import Context

		source = self.code_fixer.get_content()
		try:
			lexer = Lexer(source)
			tokens = lexer.get_tokens()
		except KeyError:
			# print("Error while parsing file:", e)
			return None
		context = Context(self.code_fixer.path.name, tokens)
		context.source = source
		return context

	def run_with_norminette(self) -> bool:
		from checker21.norminette.registry import registry
		context = self._init_norminette_context()
		if context is None:
			return False
		context.set_fix_machine(self)
		registry.run(context, getattr(context, 'source'))
		self.context = context
		return True

	def run_ast_refactoring(self) -> bool:
		from checker21.norminette.registry import registry
		context = self._init_norminette_context()
		if context is None:
			return False
		tokens = context.tokens
		registry.run(context, getattr(context, 'source'))
		ast = AST(tokens).refactor()
		# print(ast.stringify())
		self.code_fixer.set_content(ast.stringify())
		return True
