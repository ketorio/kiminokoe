import os
import requests
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, Response, stream_with_context, jsonify, session

from findsong import get_lyrics, get_track_download_url, search_yandex_music
import db_session
from data.users import User
from data.recordings import Recording

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

UPLOAD_FOLDER = 'static/recordings'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

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

        db_sess = db_session.create_session()

        existing_user = db_sess.query(User).filter(User.email == email).first()
        if existing_user:
            db_sess.close()
            return render_template('Un.html', error='Email уже зарегистрирован')

        try:
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            db_sess.add(user)
            db_sess.commit()

            session['user_id'] = user.id
            session['username'] = user.username

            db_sess.close()
            return redirect(url_for('index'))
        except Exception as e:
            db_sess.rollback()
            db_sess.close()
            return render_template('Un.html', error='Ошибка при регистрации')

    return render_template('Un.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            return render_template('login.html', error='Заполните все поля')

        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == email).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            db_sess.close()
            return redirect(url_for('index'))
        else:
            db_sess.close()
            return render_template('login.html', error='Неверный email или пароль')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('register'))


@app.route('/index')
@login_required
def index():
    return render_template('aa.html')


@app.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    tracks = []
    if query:
        tracks = search_yandex_music(query)
    return render_template('search.html', tracks=tracks, query=query)


@app.route('/song/<path:song_id>')
@login_required
def song_page(song_id):
    title = request.args.get('title', 'Неизвестная песня')
    artist = request.args.get('artist', 'Неизвестный исполнитель')
    query = request.args.get('q', '')
    lyrics = get_lyrics(song_id)

    return render_template('song.html',
                           song={'id': song_id, 'title': title, 'artist': artist},
                           lyrics=lyrics,
                           query=query)


@app.route('/stream/<path:song_id>')
@login_required
def stream_audio(song_id):
    audio_url = get_track_download_url(song_id)
    if not audio_url:
        return "Audio not available", 404

    headers = {'User-Agent': 'Mozilla/5.0'}
    resp = requests.get(audio_url, headers=headers, stream=True)
    return Response(
        stream_with_context(resp.iter_content(chunk_size=1024)),
        content_type=resp.headers.get('content-type', 'audio/mpeg')
    )


@app.route('/record', methods=['POST'])
def record():
    if 'user_id' not in session:
        return jsonify({'error': 'Не авторизован'}), 401

    if 'audio' not in request.files:
        return jsonify({'error': 'Нет аудиофайла'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'Имя файла пустое'}), 400

    track_id = request.form.get('track_id', 'unknown')
    track_title = request.form.get('track_title', 'Неизвестный трек')
    track_artist = request.form.get('track_artist', 'Неизвестный исполнитель')

    filename = f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.webm"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    db_sess = db_session.create_session()
    try:
        recording = Recording()
        recording.user_id = session['user_id']
        recording.track_id = track_id
        recording.track_title = track_title
        recording.track_artist = track_artist
        recording.filename = filename

        db_sess.add(recording)
        db_sess.commit()

        recording_id = recording.id
        db_sess.close()

        return jsonify({
            'id': recording_id,
            'filename': filename,
            'url': f'/static/recordings/{filename}',
            'message': 'Запись сохранена'
        })
    except Exception as e:
        db_sess.rollback()
        db_sess.close()
        if os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': f'Ошибка сохранения: {str(e)}'}), 500


@app.route('/recordings')
@login_required
def list_recordings():
    db_sess = db_session.create_session()

    recordings = db_sess.query(Recording).filter(
        Recording.user_id == session['user_id']
    ).order_by(Recording.created_at.desc()).all()

    recordings_list = []
    for rec in recordings:
        recordings_list.append({
            'id': rec.id,
            'filename': rec.filename,
            'track_title': rec.track_title,
            'track_artist': rec.track_artist,
            'created_at': rec.created_at.strftime('%d.%m.%Y %H:%M'),
            'url': f'/static/recordings/{rec.filename}'
        })

    db_sess.close()
    return render_template('recordings.html', recordings=recordings_list)


@app.route('/delete_recording/<int:recording_id>', methods=['POST'])
@login_required
def delete_recording(recording_id):
    db_sess = db_session.create_session()

    try:
        recording = db_sess.query(Recording).filter(
            Recording.id == recording_id,
            Recording.user_id == session['user_id']
        ).first()

        if not recording:
            db_sess.close()
            return jsonify({'error': 'Запись не найдена или нет доступа'}), 404

        filepath = os.path.join(UPLOAD_FOLDER, recording.filename)
        if os.path.exists(filepath):
            os.remove(filepath)

        db_sess.delete(recording)
        db_sess.commit()
        db_sess.close()

        return jsonify({'message': 'Запись удалена'})

    except Exception as e:
        db_sess.rollback()
        db_sess.close()
        return jsonify({'error': f'Ошибка удаления: {str(e)}'}), 500

if __name__ == '__main__':
    db_session.global_init("db/karaoke.db")
    app.run(port=8080, host='0.0.0.0', debug=True)