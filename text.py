import requests
import re

YANDEX_TOKEN = "y0__xDWobbCBxje-AYgpqjy0BZKPE4zJuFhvAP5cwIwgKp-fEOdTg"


def search_yandex_music(query):
    headers = {'Authorization': f'OAuth {YANDEX_TOKEN}',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    search_url = "https://api.music.yandex.net/search"
    params = {'text': query, 'type': 'track', 'page': '0'}
    try:
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        data = response.json()
        tracks = []
        if 'result' in data and 'tracks' in data['result']:
            for track in data['result']['tracks']['results'][:10]:
                track_id = track.get('id')
                title = track.get('title', 'Неизвестно')
                artist = track['artists'][0]['name'] if track.get('artists') else 'Неизвестный'
                duration = track.get('durationMs', 0) // 1000
                album = track.get('albums', [{}])[0].get('title', 'Яндекс.Музыка') if track.get(
                    'albums') else 'Яндекс.Музыка'
                tracks.append({
                    'id': track_id,
                    'title': title,
                    'artist': artist,
                    'album': album,
                    'duration': duration
                })
        print(f" Найдено: {len(tracks)} треков")
        return tracks
    except Exception as e:
        print(f" Ошибка поиска: {e}")
        return []


def get_track_by_id(track_id):
    headers = {'Authorization': f'OAuth {YANDEX_TOKEN}',
               'User-Agent': 'Mozilla/5.0'}
    url = f"https://api.music.yandex.net/tracks/{track_id}"
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        data = resp.json()
        track = data.get('result', [{}])[0] if data.get('result') else {}
        return {
            'id': track_id,
            'title': track.get('title', 'Неизвестно'),
            'artist': track['artists'][0]['name'] if track.get('artists') else 'Неизвестен',
            'preview_url': track.get('previewUrl'),
            'duration_ms': track.get('durationMs', 0)
        }
    except Exception as e:
        print(f"Ошибка получения трека: {e}")
        return None





def get_lyrics(track_id):
    """Возвращает список строк текста песни (без временных меток)"""
    print(f"🔍 Ищем текст для трека {track_id}...")

    # 1. LRCLIB (самый надёжный)
    try:
        track_info = get_track_by_id(track_id)
        if track_info:
            artist = track_info['artist']
            title = track_info['title']
            lrclib_url = f"https://lrclib.net/api/get?artist={requests.utils.quote(artist)}&title={requests.utils.quote(title)}"
            resp = requests.get(lrclib_url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('plainLyrics'):
                    print("✅ Получен текст с LRCLIB")
                    return data['plainLyrics'].strip().split('\n')
    except Exception as e:
        print(f"LRCLIB error: {e}")

    # 2. Яндекс (обычный текст)
    headers = {'Authorization': f'OAuth {YANDEX_TOKEN}', 'User-Agent': 'Mozilla/5.0'}
    url = f"https://api.music.yandex.net/tracks/{track_id}/lyrics"
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('result') and data['result'].get('full_lyrics'):
                print("✅ Получен текст с Яндекс")
                return data['result']['full_lyrics'].strip().split('\n')
    except Exception as e:
        print(f"Yandex lyrics error: {e}")

    # 3. Заглушка
    print("❌ Текст не найден")
    return ["Текст песни не найден", "Пойте как слышите!"]
