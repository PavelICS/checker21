from typing import Tuple

from norminette.rules.check_prototype_indent import CheckPrototypeIndent, keywords, eol
import math

from checker21.norminette.context import Context


class FixPrototypeIndent(CheckPrototypeIndent):
	def run(self, context: Context) -> Tuple[bool, int]:
		"""
		All function prototypes names must be aligned on the same indentation
		"""
		i = 0
		type_identifier_nb = -1
		current_indent = 0
		id_length = 0
		buffer_len = 0
		while context.check_token(i, ["SEMI_COLON"]) is False:
			if context.check_token(i, "IDENTIFIER") is True and context.peek_token(i).value == "__attribute__":
				i += 1
				i = context.skip_ws(i)
				i = context.skip_nest(i) + 1
				type_identifier_nb += 1
			if context.check_token(i, "LPARENTHESIS") is True:
				if context.parenthesis_contain(i)[0] == "pointer":
					i += 1
					continue
				else:
					break
			if context.check_token(i, keywords) is True:
				type_identifier_nb += 1
			i += 1
		i = 0
		while context.check_token(i, eol) is False:
			if context.check_token(i, "IDENTIFIER") is True and context.peek_token(i).value == "__attribute__":
				if type_identifier_nb > 0:
					# context.new_error("ATTR_EOL", context.peek_token(i))
					# For now do Nothing
					pass
				i += 1
				i = context.skip_ws(i)
				i = context.skip_nest(i)
				type_identifier_nb -= 1
			elif context.check_token(i, keywords) is True and type_identifier_nb > 0:
				type_identifier_nb -= 1
				if context.peek_token(i).length == 0:
					id_length += len(str(context.peek_token(i))) - 2
				else:
					id_length += context.peek_token(i).length
			elif context.check_token(i, "SPACE") is True and type_identifier_nb > 0:
				buffer_len += 1
			elif context.check_token(i, "SPACE") is True and type_identifier_nb == 0:
				# context.new_error("SPACE_REPLACE_TAB", context.peek_token(i))
				# For now do Nothing
				return True, i
			elif context.check_token(i, "TAB") is True and type_identifier_nb == 0:
				if current_indent == 0:
					current_indent = math.floor((id_length + buffer_len) / 4)
					buffer_len = 0
				current_indent += 1
			elif context.check_token(i, "IDENTIFIER") is True and type_identifier_nb == 0:
				context.add_func_decl_align(context.peek_token(i), current_indent)
				if context.scope.func_alignment == 0:
					context.scope.func_alignment = current_indent
				elif current_indent != context.scope.func_alignment:
					if current_indent > context.scope.func_alignment:
						context.scope.func_alignment = current_indent
					# context.new_error("MISALIGNED_FUNC_DECL", context.peek_token(i))
					# currently we aren't sure if its an optimal indent level
					# this error will be fixed separately
					return True, i
				return False, 0
			i += 1
		return False, 0
