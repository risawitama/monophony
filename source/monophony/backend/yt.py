import os, subprocess

import requests, ytmusicapi
from gi.repository import GLib


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


def get_similar_song(video_id: str, ignore: list = None) -> dict | None:
	yt = ytmusicapi.YTMusic()
	data = yt.get_watch_playlist(video_id, radio = True)['tracks']

	for track in data:
		if track['videoId'] != video_id:
			return {
				'title': track['title'],
				'author': track['artists'][0]['name'],
				'length': track['length'],
				'id': track['videoId'],
			}

	return None


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
	yt = ytmusicapi.YTMusic()
	if filter:
		data = yt.search(query, filter = filter)
	else:
		data = yt.search(query)
	results = []

	for result in data:
		if result['resultType'] not in {'album', 'song', 'video'}:
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
						'length': s['duration']
					} for s in album['tracks']
				]
			except:
				continue
		else:
			item['id'] = str(result['videoId'])
			item['author'] = result['artists'][0]['name']
			item['length'] = result['duration']

		results.append(item)

	return results
