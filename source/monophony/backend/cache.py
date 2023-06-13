import glob, os, subprocess

from gi.repository import GLib


def is_song_being_cached(video_id: str) -> bool:
	music_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC)
	if music_dir:
		has_temp = False
		has_part = False
		has_result = False
		for file in os.listdir(music_dir + '/monophony/'):
			parts = file.split('.')
			if parts[0] == video_id:
				if parts[-1] == 'monophony':
					has_temp = True
				elif parts[-1] == 'part':
					has_part = True
				elif parts[-1] == video_id:
					has_result = True

		if not has_result:
			return has_temp

	return False


def is_song_cached(video_id: str) -> bool:
	music_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC)
	if music_dir:
		local_path = music_dir + '/monophony/' + video_id
		return os.path.exists(local_path)

	return False


def get_song_uri(video_id: str) -> str:
	music_dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC)
	if music_dir:
		local_path = music_dir + '/monophony/' + video_id
		if os.path.exists(local_path):
			return 'file://' + local_path

	return ''


def cache_songs(ids: list):
	path = GLib.get_user_special_dir(
		GLib.UserDirectory.DIRECTORY_MUSIC
	)
	if not path:
		return
	path += '/monophony'
	os.makedirs(path, exist_ok = True)

	needed_ids = []
	for video_id in ids:
		if not is_song_cached(video_id):
			needed_ids.append(video_id)
			open(f'{path}/{video_id}.monophony', 'w').close()

	subprocess.Popen(
		f'yt-dlp -x --no-cache-dir --audio-quality 0 --add-metadata ' +
		f'-o "{path}/%(id)s.%(ext)s" https://music.youtube.com/watch?v=' +
		(' https://music.youtube.com/watch?v='.join(needed_ids)),
		shell = True,
		stdout = subprocess.PIPE
	).communicate()

	for video_id in needed_ids:
		try:
			os.remove(f'{path}/{video_id}.monophony')
		except (OSError, FileNotFoundError):
			pass

	# rename id.* files to id
	for file in glob.glob(path + '/*.*'):
		os.rename(file, '.'.join(file.split('.')[:-1]))


def uncache_song(video_id: str):
	try:
		os.remove(
			GLib.get_user_special_dir(
				GLib.UserDirectory.DIRECTORY_MUSIC
			) + '/monophony/' + video_id
		)
	except (OSError, FileNotFoundError):
		pass


def clean_up():
	music = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_MUSIC)
	if not music:
		return

	path = music + '/monophony/'
	if not os.path.exists(path):
		return

	for file in os.listdir(path):
		if file.endswith('.part'):
			os.remove(path + file)
