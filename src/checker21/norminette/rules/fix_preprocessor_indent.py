from typing import Tuple

from norminette.lexer import Token
from norminette.rules.check_preprocessor_indent import (
	CheckPreprocessorIndent, ALLOWED_PREPROC, TOO_MUCH_INDENT
)
from checker21.norminette.context import Context


class FixPreprocessorIndent(CheckPreprocessorIndent):

	def run(self, context: Context) -> Tuple[bool, int]:
		"""
		Preprocessor statements must be indented by an additionnal space for each #ifdef/#ifndef/#if
		statement.
		Structure is `#{indentation}preproc_statement`
		Preprocessor must always be at the start of the line
		"""
		tken: Token
		i = 0
		i = context.skip_ws(i)
		tken = context.peek_token(i)
		current_indent = context.preproc_scope_indent
		# ****************************** FIX ********************************* #
		# if context.peek_token(i).pos[1] != 1:
		# 	context.fix_error("PREPROC_START_LINE", 0)
		# set indent
		context.peek_token(i).indent = 0
		# ******************************************************************** #
		tken = context.peek_token(i)
		if context.check_token(i, ALLOWED_PREPROC) is False:
			# ****************************** FIX ********************************* #
			# context.new_error("PREPROC_UKN_STATEMENT", context.peek_token(i))
			# We have nothing do to with it
			pass
			# ******************************************************************** #
		if context.check_token(i, TOO_MUCH_INDENT) is True:
			current_indent -= 1
		if current_indent < 0:
			current_indent = 0
		fmt = ""
		val = tken.value[1:] if tken.value else tken.type
		spaces = self.get_space_number(tken.value if tken.value else tken.type)
		# ****************************** FIX ********************************* #
		# if current_indent != spaces:
		# 	context.fix_error("PREPROC_BAD_INDENT", i, indent=current_indent)
		# set new preproc indent to the token
		context.peek_token(i).preproc_indent = current_indent
		# ******************************************************************** #

		i += 1
		tken = context.peek_token(i)
		if tken is not None and tken.type not in ["NEWLINE", "COMMENT", "MULT_COMMENT"]:
			# ****************************** FIX ********************************* #
			# context.new_error("PREPROC_EXPECTED_EOL", context.peek_token(i))
			# We have auto fix for EOF, skip other EOL errors.
			pass
			# ******************************************************************** #
		return False, 0
