import random, subprocess

import requests, ytmusicapi


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


def search(query: str, filter: str = '') -> list:
	try:
		yt = ytmusicapi.YTMusic()
		if filter:
			data = yt.search(query, filter = filter)
		else:
			data = yt.search(query)
	except:
		return []

	results = []
	for result in data:
		if result['resultType'] not in {'album', 'song', 'video', 'playlist'}:
			continue

		item = {'type': result['resultType'], 'title': result['title']}
		if result['resultType'] == 'album':
			try:
				album = yt.get_album(result['browseId'])
				item['author'] = result['artists'][0]['name']
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
		elif result['resultType'] == 'playlist':
			try:
				album = yt.get_playlist(result['browseId'])
				item['author'] = result['author']
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
		else:
			item['id'] = str(result['videoId'])
			item['author'] = result['artists'][0]['name']
			item['length'] = result['duration']
			item['thumbnail'] = result['thumbnails'][0]['url']

		results.append(item)

	return results
