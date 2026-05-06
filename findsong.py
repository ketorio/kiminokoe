import requests
from yandex_music import Client
import re
import html
from config import YANDEX_TOKEN, GENIUS_TOKEN
from lyricsgenius import Genius

GENIUS_API = "https://api.genius.com"
TRASH_WORDS = [
    'Deutsch', 'Türkçe', 'Español', 'Français', 'Português', 'Italiano',
    'Polski', 'Русский', 'Русский (Russian)', 'Українська', 'Česky',
    'Svenska', 'العربية', 'فارسی', 'עברית', 'עברית (Hebrew)',
    'हिन्दी', 'हिन्दी (Hindi)', 'srpski', 'Български', 'azərbaycan',
    'ไทย', 'ไทย (Thai)', 'Romanization', 'English', 'Korean',
    'Contributors', 'Translations'
]


def search_yandex_music(query):
    """Поиск треков через Яндекс.Музыку"""
    headers = {
        'Authorization': f'OAuth {YANDEX_TOKEN}',
        'User-Agent': 'Mozilla/5.0'
    }
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
        print(f"Ошибка поиска: {e}")
        return []


def get_track_download_url(track_id):
    """Получение прямой ссылки на аудиофайл"""
    try:
        client = Client(YANDEX_TOKEN).init()
        track = client.tracks([track_id])[0]
        download_info = track.get_download_info(get_direct_links=True)
        if download_info:
            best = max(download_info, key=lambda x: x.bitrate_in_kbps)
            return best.direct_link
    except Exception as e:
        print(f"Ошибка получения ссылки: {e}")
    return None


def get_track_info(track_id):
    """Получение названия и исполнителя трека"""
    headers = {
        'Authorization': f'OAuth {YANDEX_TOKEN}',
        'User-Agent': 'Mozilla/5.0'
    }
    url = f"https://api.music.yandex.net/tracks/{track_id}"
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        data = resp.json()
        track = data.get('result', [{}])[0] if data.get('result') else {}
        if track:
            return {
                'title': track.get('title', 'Неизвестно'),
                'artist': track['artists'][0]['name'] if track.get('artists') else 'Неизвестен'
            }
    except Exception as e:
        print(f"Ошибка: {e}")
    return None


def clean_html_text(text):
    """Очищает текст от HTML-сущностей и лишних символов"""
    import html
    # Декодируем HTML сущности
    text = html.unescape(text)
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_trash_line(line):
    """Проверяет, является ли строка мусорной"""
    line = line.strip()

    if not line:
        return True

    if re.match(r'^\d+$', line):
        return True

    if re.match(r'^\d+\s*\([^)]*\)\s*\d+$', line):
        return True

    if re.search(r'\bContributor', line):
        return True

    if re.match(r'^\d+\s*Contributors?$', line):
        return True

    if line.lower() in ['lyrics', 'lyric']:
        return True

    if line in TRASH_WORDS:
        return True

    if re.match(r'^\d+\s*Translations?$', line):
        return True

    if re.match(r'^\[.*\]$', line) and len(line) < 30:
        return True

    if 'Embed' in line and len(line) < 20:
        return True

    return False



def get_lyrics_from_genius_api(artist, title):
    try:
        genius = Genius(GENIUS_TOKEN)
        genius.remove_section_headers = False
        genius.skip_non_songs = False
        
        song = genius.search_song(title, artist)
        
        if song:
            # Получаем текст и разбиваем на строки
            raw_lines = song.lyrics.split('\n')
            
            # Очищаем строки
            cleaned_lines = []
            for line in raw_lines:
                line = line.strip()
                
                if not line:
                    continue
                
                if re.match(r'^\[.*\]$', line):
                    continue
                
                if re.match(r'^\d+$', line):
                    continue
                
                if is_trash_line(line):
                    continue
                
                cleaned_lines.append(line)
            
            return cleaned_lines if cleaned_lines else None
            
    except Exception as e:
        print(f"Ошибка Genius API: {e}")
    
    return None


def get_lyrics(track_id):
    print(f"🔍 Ищем текст для трека {track_id}...")

    # Получаем информацию о треке
    track_info = get_track_info(track_id)
    if not track_info:
        print("❌ Не удалось получить информацию о треке")
        return ["Текст песни не найден"]

    artist = track_info['artist']
    title = track_info['title']
    print(f"🎵 Трек: {artist} - {title}")

    # 1. Пробуем Genius
    if GENIUS_TOKEN and GENIUS_TOKEN != "твой_токен_здесь":
        lyrics = get_lyrics_from_genius_api(artist, title)
        if lyrics:
            return lyrics

    # 2. Пробуем Яндекс
    try:
        headers = {
            'Authorization': f'OAuth {YANDEX_TOKEN}',
            'User-Agent': 'Mozilla/5.0'
        }
        url = f"https://api.music.yandex.net/tracks/{track_id}/lyrics"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('result') and data['result'].get('full_lyrics'):
                print("✅ Текст через Яндекс")
                return data['result']['full_lyrics'].strip().split('\n')
    except:
        pass

    # Если ничего не нашли
    print("❌ Текст не найден")
    return ["Текст песни не найден", "Попробуйте другую песню"]
