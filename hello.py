from flask import Flask, redirect, url_for, render_template, request, jsonify, escape
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import requests
import os
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from pprint import pprint
from inspect import getmembers
import json

app = Flask(__name__)
app._static_folder = 'static'

mysql = MySQL()

app.config.from_pyfile('config.py', silent=True)

mysql = MySQL(cursorclass=DictCursor)
mysql.init_app(app)

app.secret_key = b"random bytes representing flask secret key2"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = app.config["DEV"]

oauth = DiscordOAuth2Session(app)

@app.route('/register', methods=['POST', 'GET'])
@requires_authorization
def register():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        error = None

        login      = request.form['login']
        password   = request.form['password']
        typeMc     = request.form['type']
        age        = request.form['age']
        from_about = request.form['from_about']
        you_about  = request.form['you_about']
        servers    = request.form['servers']

        if not login:
            return jsonify( { 'error': 'Не указан логин' } )
        if not password:
            return jsonify( { 'error': 'Не указан пароль' } )
        if not typeMc:
            return jsonify( { 'error': 'Не указан тип аккаунта' } )
        if not age:
            return jsonify( { 'error': 'Не указан возвраст' } )
        if len(password) < 8:
            return jsonify( { 'error': 'Пароль должен быть минимум из 8 символов' } )

        user = oauth.fetch_user()
        userJson = user.to_json()

        cursor.execute("SELECT id FROM users WHERE username = %s", ( str(user.id), ))
        user_id = cursor.fetchone()

        if user_id is not None:
            return jsonify( { 'error': 'Такой пользователь уже существует' } )

        cursor.execute( 
            'INSERT INTO users (username, password, tag, type, age, from_about, you_about, status, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                ( login, password, str(userJson), typeMc, age, from_about, you_about, 1, str(userJson['id']) )
        )  
        conn.commit()
        
        ticket = 'Игровой ник: ' + login + '\n'
        ticket = ticket + 'Аккаунт: ' + ('Лицензия' if type else 'Пиратка') + '\n'
        ticket = ticket + 'Ваш возраст: ' + age + '\n'
        ticket = ticket + 'Предыдущие сервера: ' + servers + '\n'
        ticket = ticket + 'Откуда узнали о проекте: ' + from_about + '\n'
        ticket = ticket + 'Интересы в Minecraft: ' + you_about + '\n'
        ticket = ticket + 'Дискорд тэг: ' + userJson['username'] + '#' + userJson['discriminator']

        if app.config["DEV"] == "true":
            ticket = ticket + "\nЭто тестовая заявка"

        data = {
            "content" : "```" + ticket + "```",
            "username" : 'applicant'
        }

        result = requests.post(app.config["WEBHOOKURL"], json = data)

        return jsonify({'success': 'Вы успешно зарегистрировались'})
    
    return jsonify({'error': 'При регистрации произошка ошибка'})

@app.route('/')
def index():
    auth_ok = 0
    user = {}

    if oauth.authorized:
        auth_ok = 1
        user = oauth.fetch_user()

    return render_template('index.html', user=user, auth_ok=auth_ok)

@app.route("/login/")
def login():
    return oauth.create_session()

@app.route("/callback/")
def callback():
    oauth.callback()
    return redirect(url_for(".me"))

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))

	
@app.route("/me/")
@requires_authorization
def me():
    user = oauth.fetch_user()

    #перенести на клиент
    guilds = oauth.request('/users/@me/guilds')

    gmg_ok = 0

    for guild in guilds:
        if guild['id'] == '723912565234728972':
            gmg_ok = 1

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, tag, status FROM users WHERE user_id = %s", ( str(user.id), ))

    user_id = cursor.fetchone()
    # userJson = json.loads( user_id[2].replace("'",'"').replace("True", "true").replace("False", "false") )

    users = []
    
    if str(user.id) in app.config["PERMISSIONS"]:
        cursor.execute("SELECT id, username, age FROM users WHERE status = 1")

        users = cursor.fetchall()

    cursor.execute("SELECT * FROM markers WHERE user = '" + str(user.id) + "'")
    markers = cursor.fetchall()

    return render_template('me.html', gmg_ok=gmg_ok, user=user, auth_ok=1, user_id=user_id, users=users, markers=markers)

@app.route('/add_marker', methods=['POST', 'GET'])
@requires_authorization
def add_marker():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        error = None

        server      = request.form['server']
        id_type     = request.form['id_type']
        name        = request.form['name']
        x           = request.form['x']
        y           = request.form['y']
        z           = request.form['z']
        description = request.form['description']

        edit = 0
        markerID = 0

        if 'edit' in request.form:
            edit        = request.form['edit']
            markerID    = request.form['markerID']

        if not server or not id_type or not name or not x or not y or not z:
            return jsonify( { 'error': 'Не заполнены обязательные поля' } )

        user = oauth.fetch_user()

        if edit:
            cursor.execute( 
                'UPDATE markers SET id_type = %s, x = %s, y = %s, z = %s, name = %s, description = %s, server = %s, flag = %s WHERE id = %s AND user = %s',
                    ( id_type, x, y, z, name, description, server, 1, markerID, str(user.id) )
            )  
        else:
            cursor.execute( 
                'INSERT INTO markers (id_type, x, y, z, name, description, user, server, flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                    ( id_type, x, y, z, name, description, str(user.id), server, 1)
            )  
        
        conn.commit()

        return jsonify({'success': cursor.lastrowid})
    
    return jsonify({'error': 'При добавлении метки произошла ошибка'})

@app.route('/del_marker', methods=['POST', 'GET'])
@requires_authorization
def del_marker():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        error = None

        idMarker = request.form['id']
        print(idMarker)

        if not idMarker:
            return jsonify( { 'error': 'Нет ID' } )

        user = oauth.fetch_user()

        cursor.execute( 
            'DELETE FROM markers WHERE id = %s AND user = %s', 
                ( idMarker, str(user.id) )
        )  
        conn.commit()

        return jsonify({'success': 'Маркер удален'})

@app.route("/<page>/")
def start(page):
    auth_ok = 0
    user = {}

    if oauth.authorized:
        auth_ok = 1
        user = oauth.fetch_user()
    
    template = 'start.html'

    if page:
        template = page + '.html'
    
    return render_template(template, user=user, auth_ok=auth_ok)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
