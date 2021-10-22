from norminette.rules.check_line_indent import CheckLineIndent
from norminette.scope import GlobalScope


class FixLineIndent(CheckLineIndent):
	def run(self, context):
		"""
		Each new scope (function, control structure, struct/enum type declaration) adds a tab to the general indentation
		"""
		expected = context.scope.indent
		if (
			context.history[-1] == "IsEmptyLine"
			or context.history[-1] == "IsComment"
			or context.history[-1] == "IsPreprocessorStatement"
		):
			return False, 0
		if (
			context.history[-1] != "IsPreprocessorStatement"
			and type(context.scope) is GlobalScope
			and context.scope.include_allowed == True
		):
			context.scope.include_allowed = False
		got = 0
		while context.check_token(got, "TAB"):
			got += 1
		if context.check_token(got, ["LBRACE", "RBRACE"]) and expected > 0:
			if context.check_token(got, "RBRACE") is True:
				expected -= 1
			else:
				hist = context.history[: len(context.history) - 1]
				for item in hist[::-1]:
					if item == "IsEmptyLine" or item == "IsComment" or item == "IsPreprocessorStatement":
						continue
					if item not in [
						"IsControlStatement",
						"IsFuncDeclaration",
						"IsUserDefinedType",
					]:
						break
					else:
						expected -= 1
					break
		if expected > got:
			# ****************************** FIX ********************************* #
			# context.new_error("TOO_FEW_TAB", context.peek_token(0))
			# set indent
			context.peek_token(got).indent = expected
			# ******************************************************************** #
			return False, got
		elif got > expected:
			# ****************************** FIX ********************************* #
			# context.new_error("TOO_MANY_TAB", context.peek_token(0))
			# set indent
			context.peek_token(got).indent = expected
			# ******************************************************************** #
			return False, got
		return False, 0
