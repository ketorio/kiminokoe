import requests
from yandex_music import Client

YANDEX_TOKEN = "y0__xDWobbCBxje-AYgpqjy0BZKPE4zJuFhvAP5cwIwgKp-fEOdTg"


def search_yandex_music(query):
    headers = {'Authorization': f'OAuth {YANDEX_TOKEN}',
               'User-Agent': 'Mozilla/5.0'}
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
        return tracks
    except Exception as e:
        print(f"Ошибка: {e}")
        return []


def get_track_download_url(track_id):
    """Получение прямой ссылки на аудиофайл через yandex-music"""
    try:
        client = Client(YANDEX_TOKEN).init()
        # track_id имеет формат "12345:67890"
        track = client.tracks([track_id])[0]
        # Получаем информацию о доступных форматах
        download_info = track.get_download_info(get_direct_links=True)
        if download_info:
            # Берём первый доступный вариант (обычно mp3 192kbps)
            best = max(download_info, key=lambda x: x.bitrate_in_kbps)
            return best.direct_link
    except Exception as e:
        print(f"Ошибка получения ссылки: {e}")
    return None


def get_lyrics(track_id):
    """Получение синхронизированного текста (LRC)"""
    headers = {'Authorization': f'OAuth {YANDEX_TOKEN}',
               'User-Agent': 'Mozilla/5.0'}
    url = f"https://api.music.yandex.net/tracks/{track_id}/lyrics"
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        data = resp.json()
        if data.get('result'):
            lyrics_data = data['result']
            if lyrics_data.get('synchronized_lyrics'):
                return parse_lrc(lyrics_data['synchronized_lyrics'])
            elif lyrics_data.get('full_lyrics'):
                return create_simple_lyrics(lyrics_data['full_lyrics'])
    except Exception as e:
        print(f"Ошибка текста: {e}")
    # Заглушка
    return [{'time': 0, 'text': 'Текст песни не найден'}]


def parse_lrc(lrc_text):
    import re
    lines = []
    for line in lrc_text.strip().split('\n'):
        matches = re.findall(r'\[(\d+):(\d+\.\d+)\]', line)
        if matches:
            text = re.sub(r'\[.*?\]', '', line).strip()
            if text:
                for match in matches:
                    minutes = int(match[0])
                    seconds = float(match[1])
                    time_sec = minutes * 60 + seconds
                    lines.append({'time': time_sec, 'text': text})
    return sorted(lines, key=lambda x: x['time'])


def create_simple_lyrics(text):
    lines = []
    for i, line in enumerate(text.split('\n')):
        if line.strip():
            lines.append({'time': i * 5, 'text': line.strip()})
    return lines
