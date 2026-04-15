import requests


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
        print(f" Ошибка: {e}")
        return []


#search_zaycev_songs = search_yandex_music