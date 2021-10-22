from norminette.rules.check_operators_spacing import (
	CheckOperatorsSpacing, operators, lnests, rnests, glued_operators, ps_operators, gps_operators, s_operators,
	son_operators, p_operators, whitespaces, c_operators
)


class FixOperatorsSpacing(CheckOperatorsSpacing):
	def check_prefix(self, context, pos):
		tmp = -1

		if pos > 0 and context.check_token(pos, ["TAB", "SPACE"]):
			print("TODO", "???", 12, context.peek_token(pos), context.peek_token(pos).pos)
			context.new_error("", context.peek_token(pos))
		if pos + 1 < len(context.tokens[: context.tkn_scope]) and context.peek_token(pos + 1).type == "SPACE":
			print("TODO", "NO_SPC_AFR_OPR", 15, context.peek_token(pos), context.peek_token(pos).pos)
			context.new_error("NO_SPC_AFR_OPR", context.peek_token(pos))

	def check_lnest(self, context, pos):
		if context.history[-1] == "IsFuncDeclaration" or context.history[-1] == "IsFuncPrototype":
			return False
		tmp = pos + 1
		# Here is `(_`
		while context.peek_token(tmp) and context.check_token(tmp, ["SPACE", "TAB"]) is True:
			tmp += 1
		if context.check_token(tmp, "NEWLINE") is False:
			if context.check_token(tmp, lnests + rnests + ["SEMI_COLON", "PTR", "DOT"]) is True and tmp != pos + 1:
				# ****************************** FIX ********************************* #
				# context.new_error("SPC_AFTER_PAR", context.peek_token(pos))
				# add space
				print("TODO", "SPC_AFTER_PAR", 28, context.peek_token(pos), context.peek_token(pos).pos)
				# ******************************************************************** #
			elif context.check_token(tmp, lnests + rnests + ["SEMI_COLON", "PTR", "DOT"]) is False and tmp != pos + 1:
				# ****************************** FIX ********************************* #
				# context.new_error("NO_SPC_AFR_PAR", context.peek_token(pos))
				# delete all spaces
				context.delete_after(pos, ["SPACE", "TAB"])
				# ******************************************************************** #
		tmp = pos - 1
		# Here is `_(`
		while tmp >= 0 and context.check_token(tmp, ["SPACE", "TAB"]) is True:
			tmp -= 1
		if context.check_token(tmp, "NEWLINE") is False:
			if (
					context.check_token(
						tmp,
						lnests
						+ rnests
						+ [
							"SEMI_COLON",
							"PTR",
							"DOT",
							"INC",
							"DEC",
							"MULT",
							"BWISE_AND",
							"IDENTIFIER",
							"SIZEOF",
						],
					)
					is True
					and tmp != pos - 1
			):
				if context.check_token(tmp, ["MULT", "BWISE_AND"]) is True and context.is_operator == False:
					print("TODO", "NO_SPC_BFR_PAR", 54, context.peek_token(pos), context.peek_token(pos).pos)
					context.new_error("NO_SPC_BFR_PAR", context.peek_token(pos))
			elif (
					context.check_token(
						tmp,
						lnests
						+ rnests
						+ [
							"SEMI_COLON",
							"PTR",
							"DOT",
							"INC",
							"DEC",
							"MULT",
							"BWISE_AND",
							"BWISE_OR",
							"BWISE_XOR",
							"BWISE_NOT",
							"IDENTIFIER",
							"SIZEOF",
							"NOT",
							"MINUS",
							"PLUS",
							"CONSTANT",
							"CHAR_CONSTANT",
							"STRING"
						],
					)
					is False
					and tmp == pos - 1
			):
				# ****************************** FIX ********************************* #
				# context.new_error("SPC_BFR_PAR", context.peek_token(pos))
				# add space
				context.peek_token(pos - 1).to_add_space_after = True
				# ******************************************************************** #
		return False

	def check_rnest(self, context, pos):
		if context.history[-1] == "IsFuncDeclaration" or context.history[-1] == "IsFuncPrototype":
			return False
		tmp = pos + 1
		# Here is `)_`
		while context.peek_token(tmp) and context.check_token(tmp, ["SPACE", "TAB"]) is True:
			tmp += 1
		if context.check_token(tmp, "NEWLINE") is False:
			if (
					context.check_token(tmp, lnests + rnests + ["SEMI_COLON", "PTR", "DOT", "INC", "DEC"]) is True
					and tmp != pos + 1
			):
				# ****************************** FIX ********************************* #
				# context.new_error("NO_SPC_AFR_PAR", context.peek_token(pos))
				# delete all spaces
				context.delete_after(pos, ["SPACE", "TAB"])
				# ******************************************************************** #
			elif (
					context.check_token(
						tmp,
						lnests
						+ rnests
						+ [
							"SEMI_COLON",
							"PTR",
							"DOT",
							"INC",
							"DEC",
							"MINUS",
							"MULT",
							"BWISE_AND",
							"IDENTIFIER",
							"COMMA",
							"STRING",
							"CONSTANT",
							"PLUS"
						],
					)
					is False
					and tmp == pos + 1
			):
				# ****************************** FIX ********************************* #
				# context.new_error("SPC_AFTER_PAR", context.peek_token(pos))
				# add space
				context.peek_token(pos).to_add_space_after = True
				# ******************************************************************** #
		tmp = pos - 1
		# Here is `_)`
		while tmp > 0 and context.check_token(tmp, ["SPACE", "TAB"]) is True:
			tmp -= 1
		if context.check_token(tmp, "NEWLINE") is False:
			if (
					context.check_token(
						tmp,
						lnests
						+ rnests
						+ [
							"SEMI_COLON",
							"PTR",
							"DOT",
							"INC",
							"DEC",
							"MULT",
							"BWISE_AND",
							"IDENTIFIER",
						],
					)
					is True
					and tmp != pos - 1
			):
				# ****************************** FIX ********************************* #
				# context.new_error("NO_SPC_BFR_PAR", context.peek_token(pos))
				# delete all spaces
				context.delete_before(pos, ["SPACE", "TAB"])
				# ******************************************************************** #
		return False

	def check_suffix(self, context, pos):
		if pos + 1 < len(context.tokens[: context.tkn_scope]) and not context.check_token(
				pos + 1, ["SPACE", "NEWLINE", "TAB"] + glued_operators + rnests
		):
			# ****************************** FIX ********************************* #
			# context.new_error("SPC_AFTER_OPERATOR", context.peek_token(pos))
			context.peek_token(pos).to_add_space_after = True
			# ******************************************************************** #
		if pos > 0 and context.peek_token(pos - 1).type == "SPACE":
			# ****************************** FIX ********************************* #
			# context.new_error("NO_SPC_BFR_OPR", context.peek_token(pos))
			# delete space
			context.delete_before(pos, ["SPACE"])
			# ******************************************************************** #

	def check_glued_prefix_and_suffix(self, context, pos):
		if pos > 0 and context.peek_token(pos - 1).type != "SPACE":
			if context.check_token(pos - 1, "TAB") is True:
				tmp = -1
				while context.check_token(pos + tmp, "TAB") is True:
					tmp -= 1
				if context.check_token(pos + tmp, ["NEWLINE", "ESCAPED_NEWLINE"] + glued_operators) is True:
					return False, 0
			# ****************************** FIX ********************************* #
			# context.new_error("SPC_BFR_OPERATOR", context.peek_token(pos))
			# add space
			context.peek_token(pos - 1).to_add_space_after = True
			# ******************************************************************** #
		if (
				pos + 1 < len(context.tokens[: context.tkn_scope])
				and context.check_token(pos + 1, ["SPACE", "LPARENTHESIS", "LBRACKET", "LBRACE", "NEWLINE"] + glued_operators) is False
		):
			# ****************************** FIX ********************************* #
			# context.new_error("SPC_AFTER_OPERATOR", context.peek_token(pos))
			context.peek_token(pos).to_add_space_after = True
			# ******************************************************************** #

	def check_prefix_and_suffix(self, context, pos):
		if pos > 0 and context.check_token(pos - 1, ["SPACE", "LPARENTHESIS", "LBRACKET"] + glued_operators) is False:
			if context.check_token(pos - 1, "TAB") is True:
				tmp = -1
				while context.check_token(pos + tmp, "TAB") is True:
					tmp -= 1
				if context.check_token(pos + tmp, ["NEWLINE", "ESCAPED_NEWLINE"]) is True:
					return False, 0
			if context.check_token(pos - 1, "RPARENTHESIS") and context.parenthesis_contain(context.skip_nest_reverse(pos - 1))[0] == "cast":
				return False, 0
			# ****************************** FIX ********************************* #
			# context.new_error("SPC_BFR_OPERATOR", context.peek_token(pos))
			# add space
			context.peek_token(pos - 1).to_add_space_after = True
			# ******************************************************************** #
		if (
				pos + 1 < len(context.tokens[: context.tkn_scope])
				and context.check_token(
			pos + 1,
			["SPACE", "LPARENTHESIS", "RPARENTHESIS", "LBRACKET", "RBRACKET", "NEWLINE", "COMMA"] + glued_operators)
				is False
		):
			tmp = pos - 1
			while context.check_token(tmp, ['SPACE', 'TAB']):
				tmp -= 1
			if context.check_token(tmp, "RPARENTHESIS"):
				tmp = context.skip_nest_reverse(tmp)
				if context.parenthesis_contain(tmp)[0] != "cast":
					# ****************************** FIX ********************************* #
					# context.new_error("SPC_AFTER_OPERATOR", context.peek_token(pos))
					# add space
					context.peek_token(pos).to_add_space_after = True
					# ******************************************************************** #
			elif context.check_token(tmp, glued_operators) is False:
				# ****************************** FIX ********************************* #
				# context.new_error("SPC_AFTER_OPERATOR", context.peek_token(pos))
				# add space
				context.peek_token(pos).to_add_space_after = True
				# ******************************************************************** #

	def check_glued_operator(self, context, pos):
		glued = [
			"LPARENTHESIS",
			"LBRACKET",
			"LBRACE",
		]
		if context.check_token(pos + 1, ["SPACE", "TAB"]) is True:
			# ****************************** FIX ********************************* #
			# context.new_error("SPC_AFTER_OPERATOR", context.peek_token(pos))
			# delete space
			print("WTF????")
			context.peek_token(pos + 1).to_delete = True
			# ******************************************************************** #
		pos -= 1
		if context.check_token(pos, glued + ["SPACE", "TAB"] + glued_operators) is False:
			# ****************************** FIX ********************************* #
			# context.new_error("SPC_BFR_OPERATOR", context.peek_token(pos))
			# add space after current pos because where now on the previous token (pos -= 1 above)
			context.peek_token(pos).to_add_space_after = True
			# ******************************************************************** #
		while pos >= 0 and context.check_token(pos, ["SPACE", "TAB"]) is True:
			pos -= 1
			if pos >= 0 and context.check_token(pos, glued) is True:
				# ****************************** FIX ********************************* #
				# context.new_error("NO_SPC_BFR_OPR", context.peek_token(pos))
				# delete space
				print("TODO", "NO_SPC_BFR_OPR", 237, context.peek_token(pos), context.peek_token(pos).pos)
				# context.peek_token(pos).to_delete = True
				# ******************************************************************** #

	def check_combined_op(self, context, pos):
		lpointer = [
			"SPACE",
			"TAB",
			"LPARENTHESIS",
			"LBRACKET",
			"MULT",
			"NOT",
			"RPARENTHESIS",
			"RBRACKET",
			"RBRACE",
			"MINUS",
			"PLUS",
			"BWISE_NOT",
			"BWISE_OR",
			"BWISE_AND",
			"BWISE_XOR",
		]
		lsign = operators + ["LBRACKET"]
		i = 0
		if context.peek_token(pos).type == "MULT":
			if context.check_token(pos - 1, lpointer) == False and (context.is_glued_operator(pos - 1) is True):# or context.check_token(pos - 1, c_operators) is False):
				# ****************************** FIX ********************************* #
				# context.new_error("SPC_BFR_POINTER", context.peek_token(pos))
				# delete space
				print("TODO", "SPC_BFR_POINTER", 266, context.peek_token(pos), context.peek_token(pos).pos)
				# context.peek_token(pos - 1).to_delete = True
				# ******************************************************************** #
			if context.check_token(pos + 1, ["SPACE", "TAB"]):
				# ****************************** FIX ********************************* #
				# context.new_error("SPC_AFTER_POINTER", context.peek_token(pos))
				# delete space
				context.peek_token(pos + 1).to_delete = True
				# ******************************************************************** #
			i = 1
			while context.peek_token(pos + i).type in ["MULT", "LPARENTHESIS"]:
				i += 1
				if context.peek_token(pos + i).type == "SPACE":
					# ****************************** FIX ********************************* #
					# context.new_error("SPC_AFTER_POINTER", context.peek_token(pos + i))
					# delete space
					context.peek_token(pos + i).to_delete = True
					# ******************************************************************** #
				return i

	def run(self, context):
		"""
		Some operators must be followed by a space,
		some must be only followed by a space,
		and the rest must be preceded and followed by a space.
		"""
		self.last_seen_tkn = None
		i = 0
		while i < len(context.tokens[: context.tkn_scope]):
			if context.check_token(i, ["MULT", "BWISE_AND"]) is True:
				if context.is_operator(i) is False:
					self.check_combined_op(context, i)
					i += 1
					continue
			if context.check_token(i, c_operators) is True:
				if context.is_glued_operator(i) is True:
					self.check_glued_operator(context, i)
				else:
					self.check_prefix_and_suffix(context, i)
				i += 1
				continue
			elif context.check_token(i, lnests) is True:
				self.check_lnest(context, i)
			elif context.check_token(i, rnests) is True:
				self.check_rnest(context, i)
			elif context.check_token(i, ps_operators) is True:
				self.check_prefix_and_suffix(context, i)
			elif context.check_token(i, gps_operators) is True:
				self.check_glued_prefix_and_suffix(context, i)
			elif context.check_token(i, s_operators) is True:
				self.check_suffix(context, i)
			elif context.check_token(i, son_operators) is True and context.check_token(i + 1, "NEWLINE") is False:
				self.check_suffix(context, i)
			elif context.check_token(i, p_operators) is True:
				self.check_prefix(context, i)
			if context.check_token(i, whitespaces) is False:
				self.last_seen_tkn = context.peek_token(i)
			i += 1
		return False, 0
