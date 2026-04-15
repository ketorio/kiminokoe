from flask import Flask, render_template, request, redirect, url_for
from text import search_yandex_music
import requests

app = Flask(__name__)

token = "y0__xDWobbCBxje-AYgpqjy0BZKPE4zJuFhvAP5cwIwgKp-fEOdTg"

def get_preview_url(track_id):
    """Получение URL превью трека"""
    headers = {'Authorization': f'OAuth {token}'}
    url = f"https://api.music.yandex.net/tracks/{track_id}/download-info"
    params = {'format': 'json', 'codec': 'mp3', 'bitrateInKbps': '128'}
    try:
        resp = requests.get(url, headers=headers, params=params).json()
        if resp.get('result'):
            dl_info = resp['result'][0]['downloadInfoUrl']
            return f"{dl_info}&tr=0,30000"
    except Exception as e:
        print(f"Ошибка: {e}")
    return None

SONG = {
    'id': '146708734', 
    'title': 'おどるポンポコリン',
    'artist': 'B.B.クィーンズ',
    'lyrics': [
        "なんでもかんでも みんな",
        "おどりをおどっているよ",
        "おなべの中から ボワっと",
        "インチキおじさん 登場",
        "",
        "いつだって わすれない",
        "エジソンは えらい人",
        "そんなの常識 タッタタラリラ",
        "",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ おへそがちらり",
        "タッタタラリラ",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ おどるポンポコリン",
        "ピーヒャラ ピ お腹がへったよ",
        "",
        "あの子も この子もみんな",
        "いそいで 歩いているよ",
        "でんしんばしらの かげから",
        "お笑い芸人 登場",
        "",
        "いつだって 迷わない",
        "キヨスクは 駅の中",
        "そんなの 有名 タッタタラリラ",
        "",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ ニンジンいらない",
        "タッタタラリラ",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ おどるポンポコリン",
        "ピーヒャラ ピ ブタのプータロー",
        "",
        "いつだって わすれない",
        "エジソンは えらい人",
        "そんなの常識（タッタッタッタ）タッタタラリラ",
        "",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ おへそがちらり",
        "タッタタラリラ",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ おどるポンポコリン",
        "ピーヒャラ ピ お腹がへったよ (ah, yeah)",
        "",
        "ピーヒャラ ピーヒャラ パッパパラパ",
        "ピーヒャラ ピーヒャラ おどるポンポコリン",
        "ピーヒャラ ピ お腹がへったよ (ah)"
    ],
    'timings': [
        10, 3, 3, 3, 
        4, 4, 4, 4,  
        2, 2, 2, 3, 2, 1, 1,  
        1, 2, 2, 2,  
        2, 2, 2, 2,  
        2, 2, 1, 2, 1, 2, 1,  
        1, 1, 1, 
        1, 1, 1, 1, 1, 1, 1,
        1, 1, 1
    ]
}

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

@app.route('/song')
def song_page():
    """Просто страница с одной песней"""
    preview_url = get_preview_url(SONG['id'])
    return render_template('song.html', song=SONG, preview_url=preview_url)

@app.route('/record')
def record():
    return redirect(url_for('song_page'))

@app.route('/record/setup')
def record_setup():
    pass

@app.route('/recording/<int:recording_id>', methods=['GET', 'POST'])
def recording_page(recording_id):
    pass

if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)