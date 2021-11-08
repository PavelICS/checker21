from norminette.rules.check_many_instructions import CheckManyInstructions


class FixManyInstructions(CheckManyInstructions):
	def run(self, context):
		"""
		Each instruction must be separated by a newline
		"""
		if context.peek_token(0).pos[1] > 1:
			# ****************************** FIX ********************************* #
			# context.new_error("TOO_MANY_INSTR", context.peek_token(0))
			# delete space
			context.peek_token(0).too_many_instr = True
			# ******************************************************************** #
			return False, 0
		# if context.history[-1] in ["IsFuncDeclaration", "IsFuncPrototype", "IsControlStatement"]:
		#     return False, 0
		# i = 0
		# while i < context.tkn_scope:
		#     if context.check_token(i, SEPARATORS) is True:
		#         context.new_error("TOO_MANY_INSTR", context.peek_token(0))
		#         return False, 0
		#     i += 1
		return False, 0
