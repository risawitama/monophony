import json, os

import requests


def query_api_segments(video_id: str) -> dict:
	api = 'https://sponsor.ajay.app/api/skipSegments'
	segments = {}

	try:
		text = requests.get(
			f'{api}?videoID={video_id}&category=music_offtopic&action=skip',
			timeout = 1
		).text

		for seg in json.loads(text):
			timestamps = seg['segment']
			segments[float(timestamps[0])] = float(timestamps[1])

		if segments:
			write_local_segments(video_id, segments)
	except:
		pass

	return segments


def write_local_segments(video_id: str, segments: dict):
	path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/myuzi/skips'
	os.makedirs(path, exist_ok = True)

	with open(path + '/' + video_id, 'w') as s_file:
		json.dump(segments, s_file)


def read_local_segments(video_id: str) -> dict:
	path = os.getenv(
		'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
	) + '/myuzi/skips/' + video_id

	try:
		with open(path, 'r') as s_file:
			return {float(x): float(y) for x, y in json.load(s_file).items()}
	except OSError:
		return {}


def get_segments(video_id: str) -> dict:
	segments = read_local_segments(video_id)
	if not segments:
		segments = query_api_segments(video_id)

	return segments

