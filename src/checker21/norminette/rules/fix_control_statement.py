from norminette.rules.check_control_statement import CheckControlStatement, forbidden_cs, assigns


class FixControlStatement(CheckControlStatement):
    def run(self, context):
        """
        Forbidden control structures:
            - For
            - Switch case
            - Goto
        Assignations must be done outside of control structures
        """
        i = 0
        if context.scope.name == "GlobalScope":
            context.new_error("WRONG_SCOPE", context.peek_token(0))
        while context.check_token(i, "NEWLINE") is False:
            if context.check_token(i, "SEMI_COLON") is True:
                # ****************************** FIX ********************************* #
                # context.new_error("EXP_NEWLINE", context.peek_token(i))
                context.peek_token(i).exp_newline = True
                # ******************************************************************** #
                return True, i
            if context.check_token(i, forbidden_cs) is True:
                # ****************************** FIX ********************************* #
                # context.new_error("FORBIDDEN_CS", context.peek_token(i))
                # we can nothing to do Here
                # ******************************************************************** #
                return True, i
            elif context.check_token(i, "LPARENTHESIS") is True:
                if self.check_nest(context, i) == -1:
                    return True, i
            i += 1
        if i < context.tkn_scope:
            i += 1
            indent = 0
            while context.check_token(i, ["TAB"]) is True:
                i += 1
                indent += 1
            if context.check_token(i, "SEMI_COLON") is True:
                if indent > context.scope.indent + 1:
                    # ****************************** FIX ********************************* #
                    # context.new_error("TOO_MANY_TAB", context.peek_token(i))
                    # set indent
                    context.peek_token(i).indent = context.scope.indent + 1
                    # ******************************************************************** #
                if indent < context.scope.indent + 1:
                    # ****************************** FIX ********************************* #
                    # context.new_error("TOO_FEW_TAB", context.peek_token(i))
                    # set indent
                    context.peek_token(i).indent = context.scope.indent + 1
                    # ******************************************************************** #
        return False, 0
