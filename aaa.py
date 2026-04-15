from flask import Flask, render_template, request, redirect, url_for
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

@app.route('/search/<int:song_id>')
def song_page(song_id):
    return render_template('Un2.html')

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