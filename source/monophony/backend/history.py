import json, os


### --- HISTORY FUNCTIONS --- ###


def add_song(song: dict):
	new_songs = read_songs()
	if song not in new_songs:
		new_songs.append(song)
		if len(new_songs) > 10:
			new_songs = new_songs[1:]
	write_songs(new_songs)


### --- UTILITY FUNCTIONS --- ###


def write_songs(songs: list):
	dir_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony'
	recents_path = dir_path  + '/recent_songs.json'

	try:
		with open(str(recents_path), 'w') as recents_file:
			json.dump(songs, recents_file)
	except FileNotFoundError:
		os.makedirs(str(dir_path))
		write_songs(songs)


def read_songs() -> list:
	songs_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony/recent_songs.json'

	try:
		with open(songs_path, 'r') as songs_file:
			return json.load(songs_file)
	except OSError:
		return []
