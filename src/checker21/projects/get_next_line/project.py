from checker21.core import Project
from checker21.application import app


@app.register
class GnlProject(Project):
	name = 'gnl'
	verbose_name = 'Get next line'
