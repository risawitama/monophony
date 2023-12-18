import json, os


### --- HISTORY FUNCTIONS --- ###


def add_search(query: str) -> bool:
	new_searches = read_searches()
	if query not in new_searches:
		new_searches.insert(0, query)
		if len(new_searches) > 3:
			new_searches = new_searches[:-1]

		write_searches(new_searches)
		return True

	return False


def remove_search(query: str):
	new_searches = read_searches()
	new_searches.remove(query)
	write_searches(new_searches)


def add_song(song: dict):
	new_songs = read_songs()
	if song not in new_songs:
		new_songs.append(song)
		if len(new_songs) > 10:
			new_songs = new_songs[1:]
	else:
		new_songs.remove(song)
		new_songs.append(song)

	write_songs(new_songs)


def clear_songs():
	write_songs([])


### --- UTILITY FUNCTIONS --- ###


def write_searches(searches: list):
	dir_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony'
	recents_path = dir_path  + '/recent_searches.json'

	try:
		with open(str(recents_path), 'w') as recents_file:
			json.dump(searches, recents_file)
	except FileNotFoundError:
		os.makedirs(str(dir_path))
		write_songs(searches)


def read_searches() -> list:
	recents_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony/recent_searches.json'

	try:
		with open(recents_path , 'r') as recents_file:
			return json.load(recents_file)
	except OSError:
		return []


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
