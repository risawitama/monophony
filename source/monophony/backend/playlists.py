import json, os

import monophony.backend.yt

import ytmusicapi


# playlists = {
# 	'my playlist': [
# 		{'id': 'ASvGDFQwe', 'title': 'Cool song'}
# 	]
# }

# external_playlists = [
# 	{
# 		'title': 'my playlist',
# 		'url': 'ASDFfghjklZXbcnmhjklzxbcn',
# 		'contents': [
# 			{'id': 'ASvGDFQwe', 'title': 'Cool song'}
# 		]
# 	}
# ]


### --- PLAYLIST FUNCTIONS --- ###


def add_playlist(name: str, songs: list=None):
	new_lists = read_playlists()
	name = get_unique_name(name)

	songs = songs if songs else []
	new_lists[name] = []
	for song in songs:
		if song not in new_lists[name]:
			new_lists[name].append(song)

	write_playlists(playlists=new_lists)


def add_external_playlist(playlist: dict):
	lists = read_external_playlists()
	lists.append(playlist)
	write_playlists(external_playlists=lists)


def rename_playlist(name: str, new_name: str, local: bool=True) -> bool:
	if name == new_name:
		return True
	if get_unique_name(new_name) != new_name:
		return False

	if local:
		new_lists = read_playlists()
		new_lists[new_name] = new_lists.pop(name)
		write_playlists(playlists=new_lists)
		return True

	new_lists = read_external_playlists()
	for i, playlist in enumerate(new_lists):
		if playlist['title'] == name:
			new_lists[i]['title'] = new_name
			write_playlists(external_playlists=new_lists)
			return True

	return False


def import_playlist(name: str, url: str, local: bool, overwrite: bool=False) -> bool:
	new_lists = read_playlists()
	new_ext_lists = read_external_playlists()
	songs = []
	playlist_id = url.split('list=')[-1].split('&')[0]
	is_album = playlist_id.startswith('MPREb_')

	try:
		yt = ytmusicapi.YTMusic()
		if is_album:
			album = yt.get_album(playlist_id)
			data = album['tracks']
		else:
			data = yt.get_playlist(playlist_id, limit=None)['tracks']
	except:
		print('Could not get playlist')
		return False

	for item in data:
		if not item['videoId']:
			continue

		parsed_song = {
			'title': item['title'],
			'author': item['artists'][0]['name'],
			'author_id': item['artists'][0]['id'],
			'length': item['duration'] if 'duration' in item else '',
			'id': item['videoId']
		}
		if is_album:
			parsed_song['thumbnail'] = album['thumbnails'][0]['url']
		else:
			parsed_song['thumbnail'] = item['thumbnails'][0]['url']

		if parsed_song not in songs:
			songs.append(parsed_song)

	name = get_unique_name(name) if not overwrite else name
	if local:
		new_lists[name] = songs
		write_playlists(playlists=new_lists)
	else:
		new_ext_lists = [l for l in new_ext_lists if l['title'] != name]
		new_ext_lists.append({'title': name, 'id': playlist_id, 'contents': songs})
		write_playlists(external_playlists=new_ext_lists)

	return True


def remove_playlist(name: str):
	new_lists = read_playlists()
	new_lists.pop(name)
	write_playlists(playlists=new_lists)


def remove_external_playlist(name: str):
	write_playlists(
		external_playlists=[
			l for l in read_external_playlists() if l['title'] != name
		]
	)


def update_external_playlists():
	lists = read_external_playlists()
	for playlist in lists:
		import_playlist(playlist['title'], playlist['id'], False, True)

	clean_up_playlists()


def clean_up_playlists():
	lists = read_playlists()
	ext_lists = read_external_playlists()

	new_lists = {}
	for k, l in lists.items():
		new_lists[k] = [s for s in l if s['id']]

	new_ext_lists = []
	for l in ext_lists:
		new_l = l.copy()
		new_l['contents'] = [s for s in new_l['contents'] if s['id']]
		new_ext_lists.append(new_l)

	write_playlists(playlists=new_lists, external_playlists=new_ext_lists)


### --- SONG FUNCTIONS --- ###


def add_song(song: dict, playlist: str):
	new_lists = read_playlists()
	if song not in new_lists[playlist]:
		new_lists[playlist].append(song)
	write_playlists(playlists=new_lists)


def rename_song(index: int, playlist: str, new_name: str):
	new_lists = read_playlists()
	new_lists[playlist][index]['title'] = new_name
	write_playlists(playlists=new_lists)


def swap_songs(p_name: str, i: int, j: int):
	lists = read_playlists()
	i = 0 if i >= len(lists[p_name]) else i
	j = 0 if j >= len(lists[p_name]) else j
	lists[p_name][i], lists[p_name][j] = lists[p_name][j], lists[p_name][i]
	write_playlists(playlists=lists)


def move_song(p_name: str, from_i: int, to_i: int):
	lists = read_playlists()

	to_song = lists[p_name][to_i]
	from_song = lists[p_name].pop(from_i)
	lists[p_name].insert(lists[p_name].index(to_song), from_song)

	write_playlists(playlists=lists)


def remove_song(id_: str, playlist: str):
	new_lists = read_playlists()
	new_lists[playlist] = [s for s in new_lists[playlist] if s['id'] != id_]
	write_playlists(playlists=new_lists)


### --- UTILITY FUNCTIONS --- ###


def get_unique_name(base: str) -> str:
	taken_names = (
		list(read_playlists().keys()) +
		[p['title'] for p in read_external_playlists()]
	)
	name = base

	if name in taken_names:
		i = 1
		while f'{name} ({str(i)})' in taken_names:
			i += 1

		name = f'{name} ({str(i)})'

	return name


def write_playlists(playlists: dict=None, external_playlists: list=None):
	dir_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony'
	lists_path = dir_path + '/playlists.json'
	ext_lists_path = dir_path + '/external-playlists.json'

	try:
		if playlists is not None:
			with open(str(lists_path), 'w') as lists_file:
				json.dump(playlists, lists_file)
		if external_playlists is not None:
			with open(str(ext_lists_path), 'w') as ext_lists_file:
				json.dump(external_playlists, ext_lists_file)
	except FileNotFoundError:
		os.makedirs(str(dir_path))
		write_playlists(playlists=playlists, external_playlists=external_playlists)


def read_playlists() -> dict:
	lists_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony/playlists.json'

	lists = {}
	try:
		with open(lists_path, 'r') as lists_file:
			lists = json.load(lists_file)
	except OSError:
		return {}

	updated = False
	for name, playlist in lists.items():
		for i, song in enumerate(playlist):
			if 'author_id' not in song:
				print('Updating song', song['id'])
				lists[name][i]['author_id'] = monophony.backend.yt.get_song(
					song['id']
				)['author_id']
				updated = True

	if updated:
		write_playlists(playlists=lists)

	return lists


def read_external_playlists() -> list:
	lists_path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/monophony/external-playlists.json'

	lists = []
	try:
		with open(lists_path, 'r') as lists_file:
			lists = json.load(lists_file)
	except OSError:
		return []

	return lists
