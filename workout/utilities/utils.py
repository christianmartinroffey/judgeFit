import json
import subprocess
import yt_dlp
import os


def load_movement_criteria():
    file_path = '/Users/christianroffey/PycharmProjects/judgeFit/static/config/movement_analysis_criteria.json'
    criteria = {}
    try:
        with open(file_path, 'r') as file:
            criteria = json.load(file)
    except Exception as e:
        raise Exception(f"Failed to load movement criteria: {e}")
    return criteria



def get_youtube_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'cookiesfrombrowser': ('chrome',),
        'extractor_args': {'youtube': {'player_client': ['ios']}},
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        return info['url']


def download_youtube_video(youtube_url):
    output_path = '/tmp/yt_video.mp4'

    if os.path.exists(output_path):
        os.remove(output_path)

    env = os.environ.copy()
    env['PATH'] = '/opt/homebrew/bin:' + env.get('PATH', '')

    result = subprocess.run([
        'yt-dlp',
        '--extractor-args', 'youtube:player_client=android_vr',
        '--format', 'best[ext=mp4]/best',
        '--output', output_path,
        youtube_url
    ], capture_output=True, env=env)

    if result.returncode != 0:
        raise Exception(f"yt-dlp download failed: {result.stderr.decode()}")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise Exception("Downloaded file is empty or missing")

    return output_path
