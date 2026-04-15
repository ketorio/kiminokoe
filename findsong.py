import requests
from flask import Flask

app = Flask(__name__)
token = "y0__xDWobbCBxje-AYgpqjy0BZKPE4zJuFhvAP5cwIwgKp-fEOdTg"

def get_preview_url(track_id):
    headers = {'Authorization': f'OAuth {token}'}
    url = f"https://api.music.yandex.net/tracks/{track_id}/download-info"
    params = {'format': 'json', 'codec': 'mp3', 'bitrateInKbps': '128'}
    try:
        resp = requests.get(url, headers=headers, params=params).json()
        if resp.get('result'):
            dl_info = resp['result'][0]['downloadInfoUrl']
            return f"{dl_info}&tr=0,30000"
    except Exception as e:
        print(f"Ошибка в get_preview_url: {e}")
    return None

def search_yandex_songs(query):
    headers = {'Authorization': f'OAuth {token}'}
    search_url = "https://api.music.yandex.net/search"
    params = {'text': query, 'type': 'track', 'page': '0'}
    try:
        response = requests.get(search_url, headers=headers, params=params).json()
        tracks = []
        if 'result' in response and 'tracks' in response['result']:
            for track in response['result']['tracks']['results']:
                tracks.append({
                    'id': track.get('id'),
                    'title': track['title'],
                    'artist': track['artists'][0]['name'] if track['artists'] else 'Неизвестный',
                    'album': track.get('albums', [{}])[0].get('title', 'Неизвестный альбом'),
                    'duration': track.get('durationMs', 0) // 1000,
                })
        return tracks
    except Exception as e:
        print(f"Ошибка поиска: {e}")
        return []