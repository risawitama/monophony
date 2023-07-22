import json, os


def set_value(key: str, value):
	settings = read_settings()
	settings[key] = str(value)
	write_settings(settings)


def get_value(key: str, default='') -> str:
	return read_settings().get(key, default)


def write_settings(settings: dict):
	dir_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony'
	sets_path = dir_path + '/settings.json'

	try:
		with open(str(sets_path), 'w') as sets_file:
			json.dump(settings, sets_file)
	except FileNotFoundError:
		os.makedirs(dir_path)
		write_settings(settings)


def read_settings() -> dict:
	sets_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony/settings.json'

	try:
		with open(sets_path, 'r') as sets_file:
			return json.load(sets_file)
	except OSError:
		return {}
