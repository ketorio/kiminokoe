import requests
from yandex_music import Client
import re
import html
from config import YANDEX_TOKEN, GENIUS_TOKEN

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

    # Пустые строки
    if not line:
        return True

    # Строки, содержащие только цифры (ID треков/альбомов)
    if re.match(r'^\d+$', line):
        return True

    # Строки типа "653776543965381 (gt65103lt) 653816543965377"
    if re.match(r'^\d+\s*\([^)]*\)\s*\d+$', line):
        return True

    # Строки, содержащие "Contributors" или "Contributor"
    if re.search(r'\bContributor', line):
        return True

    # Строки типа "1 Contributor" или "X Contributors"
    if re.match(r'^\d+\s*Contributors?$', line):
        return True

    # Строки типа "Lyrics" отдельно
    if line.lower() in ['lyrics', 'lyric']:
        return True

    # Названия языков и переводов
    if line in TRASH_WORDS:
        return True

    # Строки типа "X Translations"
    if re.match(r'^\d+\s*Translations?$', line):
        return True

    # Строки вида "[Instrumental Break]", "[Chorus]" и т.д.
    if re.match(r'^\[.*\]$', line) and len(line) < 30:
        return True

    # Строки с "Embed" (обычно в футере страницы)
    if 'Embed' in line and len(line) < 20:
        return True

    return False


def get_lyrics_from_genius(artist, title):
    """Получение текста с Genius"""
    try:
        # Шаг 1: Ищем песню
        search_url = f"{GENIUS_API}/search"
        headers = {'Authorization': f'Bearer {GENIUS_TOKEN}'}
        params = {'q': f"{artist} {title}"}

        resp = requests.get(search_url, headers=headers, params=params, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            hits = data.get('response', {}).get('hits', [])

            if hits:
                song_url = hits[0]['result']['url']
                print(f"🔗 Найдено на Genius: {song_url}")

                # Шаг 2: Получаем страницу с текстом
                page = requests.get(song_url, timeout=10)

                if page.status_code == 200:
                    # Ищем все блоки с текстом - улучшенный паттерн
                    pattern = r'<div[^>]*data-lyrics-container="true"[^>]*>(.*?)</div>'
                    matches = re.findall(pattern, page.text, re.DOTALL)

                    if matches:
                        all_lines = []
                        seen_lines = set()  # Для удаления дубликатов

                        for match in matches:
                            # Убираем HTML теги
                            clean = re.sub(r'<[^>]+>', '\n', match)

                            # Убираем <br/> и другие варианты
                            clean = re.sub(r'<br\s*/?>', '\n', clean)

                            # Декодируем HTML сущности
                            clean = html.unescape(clean)

                            # Заменяем специальные HTML сущности
                            clean = clean.replace('&quot;', '"')
                            clean = clean.replace('&amp;', '&')
                            clean = clean.replace('&#x27;', "'")
                            clean = clean.replace('&lt;', '<')
                            clean = clean.replace('&gt;', '>')
                            clean = clean.replace('&apos;', "'")
                            clean = clean.replace('&nbsp;', ' ')

                            # Разбиваем на строки и чистим
                            for line in clean.split('\n'):
                                line = clean_html_text(line)

                                # Пропускаем мусор
                                if is_trash_line(line):
                                    continue

                                # Пропускаем дубликаты строк
                                if line in seen_lines:
                                    continue

                                seen_lines.add(line)
                                all_lines.append(line)

                        # Фильтруем строки с музыкальными обозначениями
                        filtered_lines = []
                        for line in all_lines:
                            # Пропускаем строки вида [Verse], [Chorus], [Outro]
                            if re.match(
                                    r'^\[(Verse|Chorus|Bridge|Outro|Intro|Hook|Pre-Chorus|Interlude|Refrain|Break|Solo|Drop|Build|End)\]',
                                    line, re.IGNORECASE):
                                continue
                            filtered_lines.append(line)

                        # Убираем пустые строки в начале и конце
                        while filtered_lines and not filtered_lines[0]:
                            filtered_lines.pop(0)
                        while filtered_lines and not filtered_lines[-1]:
                            filtered_lines.pop()

                        if filtered_lines:
                            print(f"✅ Текст получен через Genius! ({len(filtered_lines)} строк)")
                            return filtered_lines
    except Exception as e:
        print(f"Ошибка Genius: {e}")
        import traceback
        traceback.print_exc()

    return None


def get_lyrics(track_id):
    """Основная функция получения текста песни"""
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
        lyrics = get_lyrics_from_genius(artist, title)
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
