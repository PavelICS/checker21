
__all__ = ('get_project_name', )

aliases = {

}


def get_project_name(alias):
	alias = alias.strip(" _\t\r\n").lower()
	return aliases.get(alias, alias)
