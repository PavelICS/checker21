from norminette.rules.check_expression_statement import CheckExpressionStatement, kw


class FixExpressionStatement(CheckExpressionStatement):
	def run(self, context):
		"""
		C keywords (return, break, continue...) must be followed by a space, with the
		exception of sizeof
		Return values in a function must be contained in parenthesis
		"""
		i = 0
		parenthesis = False
		while context.check_token(i, ["SEMI_COLON", "NEWLINE"]) is False:
			if context.check_token(i, kw) is True:
				if context.check_token(i + 1, ["SPACE", "NEWLINE", "RPARENTHESIS", "COMMENT", "MULT_COMMENT"]) is False:
					# ****************************** FIX ********************************* #
					# context.new_error("SPACE_AFTER_KW", context.peek_token(i))
					# add a space after
					context.peek_token(i).to_add_space_after = True
					# ******************************************************************** #
			if context.check_token(i, ["MULT", "BWISE_AND"]) is True and i > 0:
				if context.check_token(i - 1, "IDENTIFIER") is True:
					# ****************************** FIX ********************************* #
					# context.new_error("SPACE_AFTER_KW", context.peek_token(i - 1))
					# add a space after
					context.peek_token(i - 1).to_add_space_after = True
					# ******************************************************************** #
			if context.check_token(i, "RETURN") is True:
				tmp = i + 1
				tmp = context.skip_ws(tmp)
				start = tmp
				if (
					context.check_token(tmp, "SEMI_COLON") is False
					and context.check_token(tmp, "LPARENTHESIS") is False
				):
					end = tmp
					while context.check_token(end, "SEMI_COLON") is False:
						end += 1
					if context.check_token(end, "SEMI_COLON"):
						context.fix_error("RETURN_PARENTHESIS", start, end=end)
					return False, 0
				elif context.check_token(tmp, "SEMI_COLON") is False:
					tmp = context.skip_nest(tmp) + 1
					if context.check_token(tmp, "SEMI_COLON") is False:
						end = tmp
						while context.check_token(end, "SEMI_COLON") is False:
							end += 1
						if context.check_token(end, "SEMI_COLON"):
							context.fix_error("RETURN_PARENTHESIS", start, end=end)
						return False, 0
			i += 1
		return False, 0
