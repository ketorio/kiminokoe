"""import requests


def get_yandex_music_chart():
    token = "y0__xDWobbCBxje-AYgpqjy0BZKPE4zJuFhvAP5cwIwgKp-fEOdTg"
    songs = []

    try:
        response = requests.get(
            "https://api.music.yandex.net/charts",
            headers={'Authorization': f'OAuth {token}'},
            params={'chart': 'top'}
        ).json()
        for block in response['result']['blocks']:
            for entity in block['entities']:
                track_data = entity['data']
                track = track_data['track']
                track_id = track['id']
                album_id = track['albums'][0]['id'] if track['albums'] else None
                full_id = f"{track_id}:{album_id}" if album_id else str(track_id)
                song = {
                    'position': track_data['chartPosition']['position'],
                    'artist': ', '.join([a['name'] for a in track['artists']]),
                    'title': track['title'],
                    'track_id': track_id,
                    'album_id': album_id,
                    'full_id': full_id
                }
                songs.append(song)

    except Exception as e:
        print(f"Ошибка: {e}")
    return songs


top_songs = get_yandex_music_chart()
print("Топ треков Яндекс Музыки:")
for song in top_songs[:]:
    print(f"{song['position']}. {song['artist']} — {song['title']}")
    print(song['full_id'])
"""