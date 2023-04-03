import random, subprocess

import requests, ytmusicapi


def _parse_results(data: list) -> list:
	try:
		yt = ytmusicapi.YTMusic()
	except:
		return []

	results = []
	expected_types = {'album', 'song', 'video', 'playlist', 'artist'}
	for result in data:
		if 'resultType' not in result or result['resultType'] not in expected_types:
			continue

		item = {
			'type': result['resultType'],
			'top': (result['category'] == 'Top result') if 'category' in result else False
		}
		if result['resultType'] == 'artist':
			try:
				if result['category'] == 'Top result':
					item['author'] = result['artists'][0]['name']
					item['id'] = result['artists'][0]['id']
				else:
					item['author'] = result['artist']
					item['id'] = result['browseId']
			except Exception as err:
				print('Failed to parse artist result:', err)
				continue
		elif result['resultType'] == 'album':
			try:
				album = yt.get_album(result['browseId'])
				item['author'] = result['artists'][0]['name']
				item['title'] = result['title']
				item['contents'] = [
					{
						'id': str(s['videoId']),
						'title': s['title'],
						'type': 'song',
						'author': s['artists'][0]['name'],
						'length': s['duration'],
						'thumbnail': album['thumbnails'][0]['url']
					} for s in album['tracks']
				]
			except Exception as err:
				print('Failed to parse album result:', err)
				continue
		elif result['resultType'] == 'playlist':
			try:
				album = yt.get_playlist(result['browseId'])
				item['author'] = result['author']
				item['title'] = result['title']
				item['contents'] = [
					{
						'id': str(s['videoId']),
						'title': s['title'],
						'type': 'song',
						'author': s['artists'][0]['name'],
						'length': s['duration'],
						'thumbnail': s['thumbnails'][0]['url']
					} for s in album['tracks']
				]
			except Exception as err:
				print('Failed to parse playlist result:', err)
				continue
		elif result['resultType'] in {'song', 'video'}:
			try:
				item['id'] = str(result['videoId'])
				item['title'] = result['title']
				item['author'] = result['artists'][0]['name']
				if 'duration' in result:
					item['length'] = result['duration']
				item['thumbnail'] = result['thumbnails'][0]['url']

				# ytm sometimes returns videos as song results when filtered
				if 'category' in result and result['category'] == 'Songs':
					item['type'] = 'song'
			except Exception as err:
				print('Failed to parse song/video result:', err)
				continue

		results.append(item)

	return results


def is_available() -> bool:
	try:
		requests.head('https://music.youtube.com')
		return True
	except:
		return False


def get_song_uri(video_id: str) -> str:
	out, _ = subprocess.Popen(
		f'yt-dlp -g -x https://music.youtube.com/watch?v={video_id}',
		shell = True,
		stdout = subprocess.PIPE
	).communicate()

	return out.decode().split('\n')[0]


def get_similar_song(video_id: str, ignore: list = None) -> dict:
	ignore = ignore if ignore else []
	try:
		yt = ytmusicapi.YTMusic()
		data = yt.get_watch_playlist(video_id, radio = True)['tracks']
	except:
		return {}

	acceptable_tracks = []
	for item in data:
		track = {
			'title': item['title'],
			'author': item['artists'][0]['name'],
			'length': item['length'],
			'id': item['videoId'],
			'thumbnail': item['thumbnail'][0]['url']
		}
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
					'id': item['videoId'],
				})

		if songs:
			results[group['title']] = songs

	return results


def get_artist(browse_id: str) -> list:
	yt = ytmusicapi.YTMusic()
	artist = yt.get_artist(browse_id)
	data = []
	for group in {'songs', 'albums', 'singles', 'videos'}:
		if group in artist:
			if group in {'songs', 'videos'}:
				content = yt.get_playlist(artist[group]['browseId'])['tracks']
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


def search(query: str, filter_: str = '') -> list:
	try:
		yt = ytmusicapi.YTMusic()
		if filter_:
			data = yt.search(query, filter = filter_)
		else:
			data = yt.search(query)
	except:
		return []

	return _parse_results(data)
