import importlib
import os
from glob import glob

path = os.path.dirname(os.path.realpath(__file__))
files = glob(path + "/fix_*.py")

rules = {}

for f in files:
    mod_name = f.split(os.path.sep)[-1].split(".")[0]
    class_name = "".join([s.capitalize() for s in mod_name.split("_")])
    module = importlib.import_module("checker21.norminette.rules." + mod_name)
    rule = getattr(module, class_name)
    rule = rule()
    rules[class_name] = rule

__all__ = ("rules", )
