from checker21.core import Project
from checker21.application import app


@app.register
class TemplateProject(Project):
	name = '{{project_name}}'
	verbose_name = '{{project_name}}'
