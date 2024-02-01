import traceback, random, subprocess

import ytmusicapi


def _parse_results(data: list) -> list:
	try:
		yt = ytmusicapi.YTMusic()
	except:
		return []

	results = []
	expected_types = {'album', 'song', 'video', 'playlist', 'artist', 'single'}
	for result in data:
		if 'resultType' not in result or result['resultType'] not in expected_types:
			continue

		if result['resultType'] == 'single':
			result['resultType'] = 'album'

		item = {'type': result['resultType'], 'top': False}
		if 'category' in result:
			item['top'] = (result['category'] == 'Top result')
			if result['category'] in ['Profiles', 'Episodes']:
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
				print('Failed to parse artist result:\033[0;33m')
				traceback.print_exc()
				print('\033[0m')
				continue
		elif result['resultType'] == 'album':
			try:
				album = yt.get_album(result['browseId'])
				item['author'] = ', '.join([a['name'] for a in result['artists']])
				item['id'] = result['browseId']
				item['title'] = result['title']
				item['contents'] = [
					{
						'id': str(s['videoId']),
						'title': s['title'],
						'type': 'song',
						'author': ', '.join([a['name'] for a in s['artists']]),
						'author_id': s['artists'][0]['id'],
						'length': s['duration'],
						'thumbnail': album['thumbnails'][0]['url']
					} for s in album['tracks'] if s['videoId']
				]
			except Exception:
				print('Failed to parse album result:\033[0;33m')
				traceback.print_exc()
				print('\033[0m')
				continue
		elif result['resultType'] == 'playlist':
			try:
				album = yt.get_playlist(result['browseId'])
				if 'author' in result:
					item['author'] = result['author']
				else:
					item['author'] = ', '.join([a['name'] for a in result['artists']])
				item['id'] = result['browseId']
				item['title'] = result['title']
				item['contents'] = [
					{
						'id': str(s['videoId']),
						'title': s['title'],
						'type': 'song',
						'author': ', '.join([a['name'] for a in s['artists']]),
						'author_id': s['artists'][0]['id'],
						'length': s['duration'],
						'thumbnail': s['thumbnails'][0]['url']
					} for s in album['tracks'] if s['videoId']
				]
			except:
				print('Failed to parse playlist result:\033[0;33m')
				traceback.print_exc()
				print('\033[0m')
				continue
		elif result['resultType'] in {'song', 'video'}:
			try:
				if not result['videoId']:
					continue
				item['id'] = str(result['videoId'])
				item['title'] = result['title']
				item['author'] = ', '.join([a['name'] for a in result['artists']])
				item['author_id'] = result['artists'][0]['id']
				if 'duration' in result:
					item['length'] = result['duration']
				item['thumbnail'] = result['thumbnails'][0]['url']

				# ytm sometimes returns videos as song results when filtered
				if 'category' in result and result['category'] == 'Songs':
					item['type'] = 'song'
			except:
				print('Failed to parse song/video result:\033[0;33m')
				traceback.print_exc()
				print('\033[0m')
				continue

		results.append(item)

	return results


def is_available() -> bool:
	try:
		ytmusicapi.YTMusic()
		return True
	except:
		return False


def get_song_uri(video_id: str) -> str | None:
	out, err = subprocess.Popen(
		f'yt-dlp -g -x --no-warnings https://music.youtube.com/watch?v={video_id}',
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
			'author': ', '.join([a['name'] for a in item['artists']]),
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
					'author': ', '.join([a['name'] for a in item['artists']]),
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
		metadata = yt.get_artist(browse_id)
		artist = {'name': metadata['name']}
		for group in ['albums', 'singles']:
			artist[group] = {}
			if 'params' in metadata[group]:
				artist[group]['results'] = yt.get_artist_albums(
					metadata[group]['browseId'], metadata[group]['params']
				)
			else:
				artist[group]['results'] = metadata[group]['results']

		for group in ['songs', 'videos', 'playlists']:
			if group in metadata:
				artist[group] = metadata[group]
			else:
				print('Artist has no', group)
	except:
		try:
			yt = ytmusicapi.YTMusic()
			artist = yt.get_user(browse_id)
		except:
			print('Could not get artist:\033[0;31m')
			traceback.print_exc()
			print('\033[0m')
			return []

	data = []
	for group in {'songs', 'albums', 'singles', 'videos', 'playlists'}:
		content = []
		if group in artist:
			if group in {'songs', 'videos'}:
				try:
					content = yt.get_playlist(artist[group]['browseId'])['tracks']
				except:
					content = artist[group]['results']
			else:
				content = []
				for alb in artist[group]['results']:
					try:
						content.append({
							'title': alb['title'],
							'browseId': (
								alb['browseId'] if 'browseId' in alb else
								alb['playlistId']
							),
							'artists': [{'name': artist['name']}]
						})
					except:
						print(f'Failed to get artist {group}:\033[0;33m')
						traceback.print_exc()
						print('\033[0m')
						continue

			for item in content:
				item['resultType'] = group[:-1]

			data.extend(content)

	return _parse_results(data)


def search(query: str, filter_: str='') -> list:
	try:
		yt = ytmusicapi.YTMusic()
		if filter_:
			data = yt.search(query, filter=filter_)
		else:
			data = yt.search(query)
	except:
		return []

	return _parse_results(data)
