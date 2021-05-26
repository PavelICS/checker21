from . import default_settings


class Settings:
	def __init__(self, global_settings):
		for setting in dir(global_settings):
			if setting.isupper():
				setattr(self, setting, getattr(global_settings, setting))


settings = Settings(default_settings)
