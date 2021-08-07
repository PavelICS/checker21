from checker21.core import Subject
from checker21.application import app
from .checkers import *


@app.register
class TemplateSubject(Subject):

	checkers = [

	]
