from flask import Flask, render_template, request, redirect, url_for, jsonify
from text import search_yandex_music  # твоя функция уже возвращает треки с ID!
import requests

app = Flask(__name__)

# Токен для Яндекс.Музыки
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

def get_track_details(track_id):
    headers = {'Authorization': f'OAuth {token}'}
    url = f"https://api.music.yandex.net/tracks/{track_id}"
    try:
        resp = requests.get(url, headers=headers).json()
        if resp.get('result'):
            track = resp['result'][0]
            return {
                'id': track['id'],
                'title': track['title'],
                'artist': track['artists'][0]['name'] if track['artists'] else 'Неизвестный',
                'album': track.get('albums', [{}])[0].get('title', 'Неизвестный альбом'),
                'duration': track.get('durationMs', 0) // 1000,
            }
    except Exception as e:
        print(f"Ошибка в get_track_details: {e}")
    return None


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        agree = request.form.get('agree')
        if not username or not email or not password or not confirm:
            return render_template('Un.html', error='Заполните все поля')
        if password != confirm:
            return render_template('Un.html', error='Пароли не совпадают')
        if not agree:
            return render_template('Un.html', error='Примите условия')
        return redirect(url_for('index'))
    return render_template('Un.html')

@app.route('/index')
def index():
    return render_template('aa.html')

@app.route('/search')
def search():
    query = request.args.get('q', '')
    tracks = []
    if query:
        tracks = search_yandex_music(query)  # используем твою функцию
        # Добавляем информацию о наличии текста
        for track in tracks:
            track['has_lyrics'] = str(track['id']) in LYRICS_DB
    return render_template('search.html', tracks=tracks, query=query)

@app.route('/song/<track_id>')
def song_page(track_id):
    """Страница караоке для конкретной песни"""
    # Получаем информацию о треке
    track_info = get_track_details(track_id)
    if not track_info:
        return "Песня не найдена", 404
    
    # Получаем превью URL
    preview_url = get_preview_url(track_id)
    
    # Проверяем, есть ли текст в базе
    lyrics_data = LYRICS_DB.get(str(track_id), {
        'lyrics': ['Текст песни', 'в процессе', 'добавления...'],
        'timings': [0, 3, 6]
    })
    
    song = {
        'id': track_id,
        'title': track_info['title'],
        'artist': track_info['artist'],
        'lyrics': lyrics_data['lyrics'],
        'timings': lyrics_data['timings'],
        'preview_url': preview_url,
        'has_full_lyrics': str(track_id) in LYRICS_DB
    }
    
    return render_template('karaoke.html', song=song)


@app.route('/record/setup')
def record_setup():
    pass

@app.route('/record')
def record():
    pass

@app.route('/recording/<int:recording_id>', methods=['GET', 'POST'])
def recording_page(recording_id):
    pass

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)