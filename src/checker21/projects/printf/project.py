from checker21.core import Project
from checker21.application import app


@app.register
class PrintfProject(Project):
	name = 'printf'
	verbose_name = 'Printf'
