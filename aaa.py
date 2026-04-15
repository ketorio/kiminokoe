import requests
from flask import Flask, render_template, request, redirect, url_for, Response, stream_with_context

from findsong import get_lyrics, get_track_download_url
from text import search_yandex_music

app = Flask(__name__)

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
        tracks = search_yandex_music(query)
    return render_template('search.html', tracks=tracks, query=query)

@app.route('/song/<path:song_id>')
def song_page(song_id):
    title = request.args.get('title', 'Неизвестная песня')
    artist = request.args.get('artist', 'Неизвестный исполнитель')
    query = request.args.get('q', '')
    lyrics = get_lyrics(song_id)

    return render_template('song.html',song={'id': song_id,'title': title,'artist': artist},lyrics=lyrics,query=query)

@app.route('/stream/<path:song_id>')
def stream_audio(song_id):
    audio_url = get_track_download_url(song_id)
    if not audio_url:
        return "Audio not available", 404

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    resp = requests.get(audio_url, headers=headers, stream=True)
    return Response(
        stream_with_context(resp.iter_content(chunk_size=1024)),
        content_type=resp.headers.get('content-type', 'audio/mpeg')
    )

import os
from datetime import datetime
from flask import jsonify

UPLOAD_FOLDER = 'static/recordings'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/record', methods=['POST'])
def record():
    if 'audio' not in request.files:
        return jsonify({'error': 'Нет аудиофайла'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'Имя файла пустое'}), 400

    filename = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({
        'filename': filename,
        'url': f'/static/recordings/{filename}',
        'message': 'Запись сохранена'
    })

@app.route('/record/setup')
def record_setup():
    pass


@app.route('/recording/<int:recording_id>', methods=['GET', 'POST'])
def recording_page(recording_id):
    pass

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)