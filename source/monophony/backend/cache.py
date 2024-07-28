import contextlib, glob, os, subprocess


### --- CACHE FUNCTIONS --- ###


def is_song_being_cached(video_id: str) -> bool:
	has_temp = False
	has_result = False
	for file in os.listdir(get_cache_directory()):
		parts = file.split('.')
		if parts[0] == video_id:
			if parts[-1] == 'monophony':
				has_temp = True
			elif parts[-1] == video_id:
				has_result = True

	if not has_result:
		return has_temp

	return False


def is_song_cached(video_id: str) -> bool:
	return os.path.exists(get_cache_directory() + video_id)


def get_song_uri(video_id: str) -> str:
	local_path = get_cache_directory() + video_id
	if os.path.exists(local_path):
		return 'file://' + local_path

	return ''


def cache_songs(ids: list):
	path = get_cache_directory()
	needed_ids = []
	for video_id in ids:
		if not is_song_cached(video_id):
			needed_ids.append(video_id)
			open(f'{path}{video_id}.monophony', 'w').close()

	subprocess.Popen(
		'yt-dlp -x '
		'--no-cache-dir --audio-quality 0 --add-metadata '
		f'-o "{path}%(id)s.%(ext)s" https://music.youtube.com/watch?v=' +
		(' https://music.youtube.com/watch?v='.join(needed_ids)),
		shell = True,
		stdout = subprocess.PIPE
	).communicate()

	for video_id in needed_ids:
		with contextlib.suppress(OSError, FileNotFoundError):
			os.remove(f'{path}{video_id}.monophony')

	# rename id.* files to id
	for file in glob.glob(path + '*.*'):
		os.rename(file, '.'.join(file.split('.')[:-1]))


def uncache_song(video_id: str):
	with contextlib.suppress(OSError, FileNotFoundError):
		os.remove(get_cache_directory() + video_id)


def clean_up():
	path = get_cache_directory()
	for file in os.listdir(path):
		if file.endswith('.part'):
			os.remove(path + file)


### --- UTILITY FUNCTIONS --- ###


def get_cache_directory() -> str:
	path = os.getenv(
		'XDG_DATA_HOME', os.path.expanduser('~/.local/share')
	) + '/monophony/'
	os.makedirs(path, exist_ok=True)
	return path
