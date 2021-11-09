from norminette.exceptions import CParsingError
from norminette.rules.check_assignation_indent import CheckAssignationIndent, operators, nest_kw


class FixAssignationIndent(CheckAssignationIndent):
    def run(self, context):
        """
        Declared variables must be aligned using tabs with other variables on the same scope
        """
        i = 0
        expected = context.scope.indent
        if context.history[-1] in ["IsAssignation", "IsVarDeclaration"]:
            nest = expected + 1
        elif context.history[-1] == "IsFuncPrototype":
            nest = context.func_alignment
        else:
            nest = expected
        while context.check_token(i, ["SEMI_COLON"]) is False:
            if context.check_token(i, "NEWLINE") is True:
                if context.check_token(i - 1, operators) is True:
                    # ****************************** FIX ********************************* #
                    # context.new_error("EOL_OPERATOR", context.peek_token(i))
                    context.peek_token(i - 1).to_add_newline_before = True
                    context.peek_token(i).to_delete = True
                    # ******************************************************************** #
                tmp = context.skip_ws(i + 1)
                if context.check_token(tmp, "COMMA"):
                    # ****************************** FIX ********************************* #
                    # context.new_error("COMMA_START_LINE", context.peek_token(i))
                    context.delete_before(i, ["SPACE", "TAB"])
                    context.peek_token(tmp).to_add_newline_after = True
                    context.peek_token(tmp).indent = 0
                    context.peek_token(i).to_delete = True
                    # ******************************************************************** #
                got = 0
                i += 1
                while context.check_token(i + got, "TAB") is True:
                    got += 1
                if context.peek_token(i + got) is None:
                    raise CParsingError(f"Error: Unexpected EOF l.{context.peek_token(i - 1).pos[0]}")
                if context.check_token(i + got, ["LBRACKET", "RBRACKET", "LBRACE", "RBRACE"]):
                    nest -= 1
                if got > nest or (got > nest + 1 and context.history[-1] in ["IsAssignation", "IsVarDeclaration"]):
                    # ****************************** FIX ********************************* #
                    # context.new_error("TOO_MANY_TAB", context.peek_token(i))
                    # set indent
                    context.peek_token(i + got).indent = nest
                    # ******************************************************************** #
                elif got < nest or (got < nest - 1 and context.history[-1] in ["IsAssignation", "IsVarDeclaration"]):
                    # ****************************** FIX ********************************* #
                    # context.new_error("TOO_FEW_TAB", context.peek_token(i))
                    # set indent
                    context.peek_token(i + got).indent = nest
                    # ******************************************************************** #
                if context.check_token(i + got, ["LBRACKET", "RBRACKET", "LBRACE", "RBRACE"]):
                    nest += 1
            if context.check_token(i, "LPARENTHESIS") is True:
                nest += 1
            if context.check_token(i, "RPARENTHESIS") is True:
                nest -= 1
            i += 1
        return False, 0
