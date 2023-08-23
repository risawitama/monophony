import traceback, random, subprocess

import ytmusicapi


def _parse_results(data: list, loader: object=None) -> list:
	try:
		yt = ytmusicapi.YTMusic()
	except:
		return []

	if loader:
		loader.lock.lock()
		loader.set_text(_('Parsing Results...'))
		loader.target = len(data)

	results = []
	expected_types = {'album', 'song', 'video', 'playlist', 'artist', 'single'}
	for result in data:
		if loader:
			loader.progress()

		if 'resultType' not in result or result['resultType'] not in expected_types:
			continue

		if result['resultType'] == 'single':
			result['resultType'] = 'album'

		item = {'type': result['resultType'], 'top': False}
		if 'category' in result:
			item['top'] = (result['category'] == 'Top result')
			if result['category'] == 'Profiles':
				continue

		if result['resultType'] == 'artist':
			try:
				if result['category'] == 'Top result':
					item['author'] = result['artists'][0]['name']
					item['id'] = result['artists'][0]['id']
				else:
					item['author'] = result['artist']
					item['id'] = result['browseId']
			except:
				print('Failed to parse artist result')
				traceback.print_exc()
				continue
		elif result['resultType'] == 'album':
			try:
				album = yt.get_album(result['browseId'])
				item['author'] = result['artists'][0]['name']
				item['id'] = result['browseId']
				item['title'] = result['title']
				item['contents'] = [
					{
						'id': str(s['videoId']),
						'title': s['title'],
						'type': 'song',
						'author': s['artists'][0]['name'],
						'author_id': s['artists'][0]['id'],
						'length': s['duration'],
						'thumbnail': album['thumbnails'][0]['url']
					} for s in album['tracks'] if s['videoId']
				]
			except Exception:
				print('Failed to parse album result')
				traceback.print_exc()
				continue
		elif result['resultType'] == 'playlist':
			try:
				album = yt.get_playlist(result['browseId'])
				item['author'] = result['author']
				item['id'] = result['browseId']
				item['title'] = result['title']
				item['contents'] = [
					{
						'id': str(s['videoId']),
						'title': s['title'],
						'type': 'song',
						'author': s['artists'][0]['name'],
						'author_id': s['artists'][0]['id'],
						'length': s['duration'],
						'thumbnail': s['thumbnails'][0]['url']
					} for s in album['tracks'] if s['videoId']
				]
			except:
				print('Failed to parse playlist result')
				traceback.print_exc()
				continue
		elif result['resultType'] in {'song', 'video'}:
			try:
				if not result['videoId']:
					continue
				item['id'] = str(result['videoId'])
				item['title'] = result['title']
				item['author'] = result['artists'][0]['name']
				item['author_id'] = result['artists'][0]['id']
				if 'duration' in result:
					item['length'] = result['duration']
				item['thumbnail'] = result['thumbnails'][0]['url']

				# ytm sometimes returns videos as song results when filtered
				if 'category' in result and result['category'] == 'Songs':
					item['type'] = 'song'
			except:
				print('Failed to parse song/video result')
				traceback.print_exc()
				continue

		results.append(item)

	if loader:
		loader.lock.unlock()

	return results


def is_available() -> bool:
	try:
		ytmusicapi.YTMusic()
		return True
	except:
		return False


def get_song_uri(video_id: str) -> str | None:
	out, err = subprocess.Popen(
		f'yt-dlp -g -x https://music.youtube.com/watch?v={video_id}',
		shell=True,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE,
	).communicate()
	if err:
		print(err.decode())
		return None

	return out.decode().split('\n')[0]


def get_similar_song(video_id: str, ignore: list=None) -> dict:
	ignore = ignore if ignore else []
	try:
		yt = ytmusicapi.YTMusic()
		data = yt.get_watch_playlist(video_id, radio=True)['tracks']
	except:
		return {}

	acceptable_tracks = []
	for item in data:
		track = {
			'title': item['title'],
			'author': item['artists'][0]['name'],
			'author_id': item['artists'][0]['id'],
			'length': item['length'],
			'id': item['videoId'],
			'thumbnail': item['thumbnail'][0]['url']
		}
		if not track['id']:
			continue

		for id_ in ignore:
			if id_ == track['id']:
				break
		else: # nobreak
			acceptable_tracks.append(track)

	if acceptable_tracks:
		return random.choice(acceptable_tracks)
	return {}


def get_recommendations() -> dict:
	try:
		yt = ytmusicapi.YTMusic()
		data = yt.get_home()
	except:
		return {}

	results = {}
	for group in data:
		songs = []
		for item in group['contents']:
			if 'videoId' in item:
				songs.append({
					'title': item['title'],
					'author': item['artists'][0]['name'],
					'author_id': item['artists'][0]['id'],
					'id': item['videoId'],
				})

		if songs:
			results[group['title']] = songs

	return results


def get_song(id_: str) -> dict:
	try:
		yt = ytmusicapi.YTMusic()
		result = yt.get_song(id_)['videoDetails']
	except:
		return {'id': id_, 'author': '', 'author_id': ''}

	return {
		'id': result['videoId'],
		'author': result['author'],
		'author_id': result['channelId'],
	}


def get_artist(browse_id: str) -> list:
	yt = None
	try:
		yt = ytmusicapi.YTMusic()
		artist = yt.get_artist(browse_id)
	except:
		print('Could not get artist')
		return []

	data = []
	for group in {'songs', 'albums', 'singles', 'videos'}:
		content = []
		if group in artist:
			if group in {'songs', 'videos'}:
				browse_id = artist[group]['browseId']
				if browse_id:
					content = yt.get_playlist(browse_id)['tracks']
			else:
				content = []
				for album in artist[group]['results']:
					content.append({
						'title': album['title'],
						'browseId': album['browseId'],
						'artists': [{'name': artist['name']}]
					})

			for item in content:
				item['resultType'] = group[:-1]

			data.extend(content)

	return _parse_results(data)


def search(query: str, filter_: str='', loader: object=None) -> list:
	if loader:
		loader.lock.lock()
	try:
		yt = ytmusicapi.YTMusic()
		if filter_:
			data = yt.search(query, filter=filter_)
		else:
			data = yt.search(query)
	except:
		if loader:
			loader.lock.unlock()
		return []

	if loader:
		loader.lock.unlock()
	return _parse_results(data, loader=loader)
