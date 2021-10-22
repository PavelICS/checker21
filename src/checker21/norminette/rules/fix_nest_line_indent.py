from norminette.rules.check_nest_line_indent import CheckNestLineIndent, operators


class FixNestLineIndent(CheckNestLineIndent):
	def find_nest_content(self, context, nest, i):
		expected = context.scope.indent + nest
		while context.peek_token(i) is not None:
			if context.check_token(i, ["LPARENTHESIS", "LBRACE", "LBRACKET"]) is True:
				i += 1
				i = self.find_nest_content(context, nest + 1, i) + 1
			if context.check_token(i, ["RBRACE", "RBRACKET", "RPARENTHESIS"]):
				return i
			elif context.check_token(i, "NEWLINE") is True:
				if context.check_token(i - 1, operators):
					# ****************************** FIX ********************************* #
					# context.new_error("EOL_OPERATOR", context.peek_token(i - 1))
					context.peek_token(i - 1).to_add_newline_before = True
					context.peek_token(i).to_delete = True
					# ******************************************************************** #
				if context.check_token(i, "SEMI_COLON") is True:
					return i
				indent = 0
				i += 1
				while context.check_token(i, "TAB") is True:
					indent += 1
					i += 1
				if context.check_token(i, ["RBRACE", "RBRACKET", "RPARENTHESIS"]):
					expected -= 1
				if indent > expected:
					# ****************************** FIX ********************************* #
					# context.new_error("TOO_MANY_TAB", context.peek_token(i))
					# set indent
					context.peek_token(i).indent = expected
					# ******************************************************************** #
				elif indent < expected:
					# ****************************** FIX ********************************* #
					# context.new_error("TOO_FEW_TAB", context.peek_token(i))
					# set indent
					context.peek_token(i).indent = expected
					# ******************************************************************** #
				if context.check_token(i, ["RBRACE", "RBRACKET", "RPARENTHESIS"]):
					expected += 1
			else:
				i += 1
		return i
