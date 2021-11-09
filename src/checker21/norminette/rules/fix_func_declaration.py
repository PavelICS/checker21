from norminette.rules.check_func_declaration import CheckFuncDeclaration, types


class FixFuncDeclaration(CheckFuncDeclaration):
	def run(self, context):
		"""
		Maximum 4 arguments in a function
		Function declaration must be preceded by a newline
		"""
		i = 0
		tmp = 0
		start = 0
		arg = 1
		while context.check_token(tmp, ["SEMI_COLON", "NEWLINE"]) is False:
			if context.check_token(tmp, "LBRACE") is True:
				# ****************************** FIX ********************************* #
				# context.new_error("BRACE_NEWLINE", context.peek_token(tmp))
				# add new line
				context.peek_token(start).to_add_newline_before = True
				# ******************************************************************** #
			tmp += 1
		# if tmp < context.tkn_scope - 2:
		# context.new_error("NEWLINE_IN_DECL", context.peek_token(tmp))
		# this is a func declaration
		if context.history[-1] == 'IsFuncDeclaration':
			#        if context.check_token(tmp, "SEMI_COLON") is False:
			i = 2
			length = len(context.history)
			while length - i >= 0 and (context.history[-i] == "IsPreprocessorStatement"
										or context.history[-i] == "IsComment"
										or context.history[-i] == "IsFuncDeclaration"
			):
				i += 1
			if length - i > 0 and context.history[-i] != "IsEmptyLine":
				# ****************************** FIX ********************************* #
				# context.new_error("NEWLINE_PRECEDES_FUNC", context.peek_token(start))
				# add new line
				context.peek_token(start).to_add_newline_before = True
				# ******************************************************************** #
		i = context.fname_pos + 1
		while (context.check_token(i, ["RPARENTHESIS"])) is True:  #, "SPACE", "TAB"])) is True:
			i += 1
		if context.check_token(i, "LPARENTHESIS") is False:
			context.new_error("EXP_PARENTHESIS", context.peek_token(i))
		i += 1
		deep = 1
		while deep > 0:
			if context.check_token(i, "LPARENTHESIS"):
				i = context.skip_nest(i)
			if context.check_token(i, "RPARENTHESIS"):
				deep -= 1
			if context.check_token(i, "COMMA"):
				arg += 1
			i += 1
		if context.check_token(i - 1, ["SPACE", "TAB"]) is True:
			tmp = i - 1
			while context.check_token(tmp, ["SPACE", "TAB"]) is True:
				tmp -= 1
			if context.check_token(tmp, "NEWLINE") is False:
				# ****************************** FIX ********************************* #
				# context.new_error("NO_SPC_BFR_PAR", context.peek_token(i))
				# delete spaces
				context.delete_before(i, ["TAB", "SPACE"])
				# ******************************************************************** #
		if arg > 4:
			# ****************************** FIX ********************************* #
			# context.new_error("TOO_MANY_ARGS", context.peek_token(i))
			# we cant help there
			pass
			# ******************************************************************** #
		arg = []
		while context.check_token(i, ["NEWLINE", "SEMI_COLON"]) is False:
			i += 1
		if context.check_token(i - 1, ["TAB", "SPACE"]):
			# ****************************** FIX ********************************* #
			# context.new_error("SPC_BEFORE_NL", context.peek_token(i))
			# delete spaces before NL / SEMI_COLON
			context.delete_before(i, ["TAB", "SPACE"])
			# ******************************************************************** #
		return False, 0
