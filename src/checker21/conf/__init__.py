import importlib

from checker21.core.exceptions import ImproperlyConfigured
from checker21.utils.functional import LazyObject, empty

from . import default_settings, environment


class LazySettings(LazyObject):
	"""
	A lazy proxy for either global Django settings or a custom settings object.
	The user can manually configure settings prior to using them. Otherwise,
	it uses the settings module pointed to by SETTINGS_MODULE var in the environment.
	"""
	def _setup(self, name=None):
		"""
		Load the settings module pointed to by the environment variable. This
		is used the first time settings are needed, if the user hasn't
		configured settings manually.
		"""
		self._wrapped = Settings(environment.SETTINGS_MODULE)

	def __repr__(self):
		# Hardcode the class name as otherwise it yields 'Settings'.
		if self._wrapped is empty:
			return '<LazySettings [Unevaluated]>'
		return f'<LazySettings "{self._wrapped.SETTINGS_MODULE}">'

	def __getattr__(self, name):
		"""Return the value of a setting and cache it in self.__dict__."""
		if self._wrapped is empty:
			self._setup(name)
		val = getattr(self._wrapped, name)
		self.__dict__[name] = val
		return val

	def __setattr__(self, name, value):
		"""
		Set the value of setting. Clear all cached values if _wrapped changes
		(@override_settings does this) or clear single values when set.
		"""
		if name == '_wrapped':
			self.__dict__.clear()
		else:
			self.__dict__.pop(name, None)
		super().__setattr__(name, value)

	def __delattr__(self, name):
		"""Delete a setting and clear it from cache if needed."""
		super().__delattr__(name)
		self.__dict__.pop(name, None)

	def configure(self, user_settings=default_settings, **options):
		"""
		Called to manually configure the settings. The 'default_settings'
		parameter sets where to retrieve any unspecified values from (its
		argument must support attribute access (__getattr__)).
		"""
		if self._wrapped is not empty:
			raise RuntimeError('Settings already configured.')
		holder = UserSettingsHolder(user_settings)
		for name, value in options.items():
			if not name.isupper():
				raise TypeError(f'The "{name}" setting must be uppercase.')
			setattr(holder, name, value)
		self._wrapped = holder

	@property
	def configured(self):
		"""Return True if the settings have already been configured."""
		return self._wrapped is not empty


class Settings:
	def __init__(self, settings_module):
		for setting in dir(default_settings):
			if setting.isupper():
				setattr(self, setting, getattr(default_settings, setting))

		self.SETTINGS_MODULE = settings_module
		if self.SETTINGS_MODULE:
			mod = importlib.import_module(self.SETTINGS_MODULE)

			tuple_settings = (

			)
			for setting in dir(mod):
				if setting.isupper():
					setting_value = getattr(mod, setting)

					if (setting in tuple_settings and
							not isinstance(setting_value, (list, tuple))):
						raise ImproperlyConfigured(f'The {setting} setting must be a list or a tuple.')
					setattr(self, setting, setting_value)

	def __repr__(self):
		return f'<{self.__class__.__name__} "{self.SETTINGS_MODULE}">'


class UserSettingsHolder:
	"""Holder for user configured settings."""
	# SETTINGS_MODULE doesn't make much sense in the manually configured
	# (standalone) case.
	SETTINGS_MODULE = None

	def __init__(self, default_settings):
		"""
		Requests for configuration variables not in this class are satisfied
		from the module specified in default_settings (if possible).
		"""
		self.__dict__['_deleted'] = set()
		self.default_settings = default_settings

	def __getattr__(self, name):
		if not name.isupper() or name in self._deleted:
			raise AttributeError
		return getattr(self.default_settings, name)

	def __setattr__(self, name, value):
		self._deleted.discard(name)
		super().__setattr__(name, value)

	def __delattr__(self, name):
		self._deleted.add(name)
		if hasattr(self, name):
			super().__delattr__(name)

	def __dir__(self):
		return sorted(
			s for s in [*self.__dict__, *dir(self.default_settings)]
			if s not in self._deleted
		)

	def __repr__(self):
		return f'<{self.__class__.__name__}>'

settings = LazySettings()
