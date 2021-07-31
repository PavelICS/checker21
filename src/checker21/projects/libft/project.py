from checker21.core import Project
from checker21.application import app


@app.register
class LibftProject(Project):
	name = 'libft'
	verbose_name = 'LibFT'
