from norminette.exceptions import CParsingError
from norminette.registry import Registry as NorminetteRegistry

from .context import Context
from .rules import rules


class Registry(NorminetteRegistry):
	def run(self, context: Context, source: str) -> None:
		"""
		Main function for each file.
		Primary rules are determined by the prefix "Is" and
		are run by order of priority as defined in each class
		Each secondary rule is then run in arbitrary order based on their
		dependencies
		"""
		unrecognized_tkns = []
		while context.tokens:
			context.tkn_scope = len(context.tokens)
			for rule in self.primary_rules:
				if type(context.scope) not in rule.scope and rule.scope != []:
					continue
				ret, jump = self.run_rules(context, rule)
				if ret is True:
					if unrecognized_tkns:
						if context.debug == 0:
							raise CParsingError(
								f"Error: Unrecognized line {unrecognized_tkns[0].pos} while parsing line {unrecognized_tkns}"
							)
						unrecognized_tkns = []
					context.dprint(rule.name, jump)
					context.update()
					context.pop_tokens(jump)
					# print(context.tokens)
					break


registry = Registry()
registry.dependencies = {}
registry.rules = rules
for rule in rules.values():
	rule.register(registry)

__all__ = ['registry']
