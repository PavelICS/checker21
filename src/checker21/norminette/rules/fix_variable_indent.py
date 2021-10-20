from norminette.rules.check_variable_indent import CheckVariableIndent


class FixVariableIndent(CheckVariableIndent):
    def run(self, context):
        """
        Each variable must be indented at the same level for its scope
        """
        i = 0
        identifier = None
        ident = [0, 0]
        ret = None
        # we don't need to check tabs any more
        # self.check_tabs(context)
        while context.peek_token(i) and context.check_token(i, ["SEMI_COLON", "COMMA", "ASSIGN"]) is False:
            if context.check_token(i, ["LBRACKET", "LBRACE"]) is True:
                i = context.skip_nest(i)
            if context.check_token(i, "LPARENTHESIS") is True:
                ret, _ = context.parenthesis_contain(i)
            if context.check_token(i, "IDENTIFIER") is True:
                ident = (context.peek_token(i), i)
                if ret == "pointer":
                    break
            i += 1
        i = ident[1]
        identifier = ident[0]
        if context.check_token(i - 1, ["MULT", "BWISE_AND", "LPARENTHESIS"]) is True:
            i -= 1
            while (
                context.check_token(i - 1, ["MULT", "BWISE_AND", "LPARENTHESIS"]) is True
                and context.is_operator(i) is False
            ):
                i -= 1
            identifier = context.peek_token(i)
        context.add_var_decl_align(identifier)
        if context.scope.vars_alignment == 0:
            context.scope.vars_alignment = identifier.pos[1]
        elif context.scope.vars_alignment != identifier.pos[1]:
            if identifier.pos[1] > context.scope.vars_alignment:
                context.scope.vars_alignment = identifier.pos[1]
            # context.new_error("MISALIGNED_VAR_DECL", context.peek_token(i))
            # currently we aren't sure if its an optimal indent level
            # this error will be fixed separately
            return True, i
        return False, 0
