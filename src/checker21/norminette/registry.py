from norminette.registry import Registry
from .rules import rules

registry = Registry()
registry.dependencies = {}
registry.rules = rules
for rule in rules.values():
	rule.register(registry)

__all__ = ['registry']
