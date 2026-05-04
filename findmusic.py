from config import token
import requests


def search_songs(artist):
    response = requests.get("https://api.music.yandex.net/search",
                            headers={'Authorization': f'OAuth {token}'},
                            params={'text': artist, 'type': 'artist', 'page': '0'}).json()

    artist_id = response['result']['artists']['results'][0]['id']

    tracks = requests.get(f"https://api.music.yandex.net/artists/{artist_id}/tracks",
                          headers={'Authorization': f'OAuth {token}'}).json()

    return [t['title'] for t in tracks['result']['tracks']]


print(search_songs('пневмослон'))
