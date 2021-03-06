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

#Регистрация
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

        cursor.execute("SELECT id FROM users WHERE username = %s", ( str(user.id) ))
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

    # перенести на клиент
    # пока такой костыль что бы как минимум не падало с 500
    try:
        guilds = oauth.request('/users/@me/guilds')
    except:
        guilds = {}

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
    all_markers = []
    opUser = 0
    
    if str(user.id) in app.config["PERMISSIONS"]:
        opUser = 1

    cursor.execute("SELECT * FROM markers WHERE user = '" + str(user.id) + "'")
    markers = cursor.fetchall()

    return render_template('me.html', gmg_ok=gmg_ok, user=user, auth_ok=1, user_id=user_id, users=users, markers=markers, opUser=opUser)

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

        if not _is_numb(x) or not _is_numb(y) or not _is_numb(z):
            return jsonify( { 'error': 'Координаты могут быть только число' } )

        user = oauth.fetch_user()

        if edit:
            cursor.execute( 
                'UPDATE markers SET id_type = %s, x = %s, y = %s, z = %s, name = %s, description = %s, server = %s, flag = %s WHERE id = %s',
                    ( id_type, x, y, z, name, description, server, 1, markerID )
            )  
        else:
            cursor.execute( 
                'INSERT INTO markers (id_type, x, y, z, name, description, user, server, flag) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                    ( id_type, x, y, z, name, description, str(user.id), server, 1)
            )

        conn.commit()

        cursor.execute(
            'INSERT INTO queue (task, status, object) VALUES (%s, %s, %s)',
                ( 'update', 'new', id_type )
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
        allmarkers = request.form['allmarkers'] if 'allmarkers' in request.form else 0

        if not idMarker:
            return jsonify( { 'error': 'Нет ID' } )

        user = oauth.fetch_user()

        where = ' AND user = "' + str(user.id) + '"'

        if str(user.id) in app.config["PERMISSIONS"] and allmarkers:
            where = ''

        cursor.execute( 'DELETE FROM markers WHERE id = ' + idMarker + where )  
        conn.commit()

        return jsonify({'success': 'Маркер удален'})

@app.route("/other_markers/")
def other_markers():
    user = oauth.fetch_user()

    if not str(user.id) in app.config["PERMISSIONS"]:
        return 'Доступ запрещен'

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT markers.*, username FROM markers join users on user = user_id order by username")
    markers = cursor.fetchall()

    return render_template('other_markers.html', user=user,  markers=markers, opUser=1, auth_ok=1)

@app.route("/list_players/")
def list_players():
    user = oauth.fetch_user()

    if not str(user.id) in app.config["PERMISSIONS"]:
        return 'Доступ запрещен'

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, age, status FROM users ORDER BY status")
    users = cursor.fetchall()

    return render_template('list_players.html', user=user, users=users, auth_ok=1)

@app.route('/change_user', methods=['POST', 'GET'])
@requires_authorization
def change_user():
    user = oauth.fetch_user()

    if not str(user.id) in app.config["PERMISSIONS"]:
        return 'Отказано в доступе'

    userID = request.form['id']
    action = request.form['action']

    if not userID or not action:
        return jsonify( { 'message': 'Нет обязательного параметра' } )

    status = 1

    if action == 'accept':
        status = 2
    elif action == 'not_accept' or action == 'unban':
        status = 3
    elif action == 'ban':
        status = 4
    
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute( "UPDATE users SET status = %s WHERE id = %s", (status, userID) )
    conn.commit()

    return jsonify( { 'message': 'Статус изменен' } )


@app.route('/add_territories', methods=['POST', 'GET'])
@requires_authorization
def add_territories():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        error = None

        name   = request.form['name']
        xStart = request.form['xStart']
        zStart = request.form['zStart']
        xStop  = request.form['xStop']
        zStop  = request.form['zStop']

        edit = 0
        markerID = 0

        if 'edit' in request.form:
            edit        = request.form['edit']
            markerID    = request.form['markerID']

        if not name or not xStart or not zStart or not xStop or not zStop:
            return jsonify( { 'error': 'Не заполнены обязательные поля' } )

        if not _is_numb(xStart) or not _is_numb(zStart) or not _is_numb(xStop) or not _is_numb(zStop):
            return jsonify( { 'error': 'Координаты могут быть только число' } )

        user = oauth.fetch_user()

        if edit:
            cursor.execute( 
                'UPDATE territories SET xStart = %s, zStart = %s, xStop = %s, name = %s, zStop = %s WHERE id = %s',
                    ( xStart, zStart, xStop, name, zStop, markerID )
            )  
        else:
            cursor.execute("SELECT id FROM territories WHERE name = %s", ( name ) )
            terr = cursor.fetchone()

            if terr is not None:
                return jsonify( { 'error': 'Такая метка уже существует' } )

            cursor.execute( 
                'INSERT INTO territories (xStart, zStart, xStop, zStop, name, user) VALUES (%s, %s, %s, %s, %s, %s)', 
                    ( xStart, zStart, xStop, zStop, name, str(user.id))
            )  
        
        conn.commit()

        return jsonify({'success': cursor.lastrowid})
    
    return jsonify({'error': 'При добавлении метки произошла ошибка'})

@app.route('/del_territories', methods=['POST', 'GET'])
@requires_authorization
def del_territories():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        error = None

        idMarker = request.form['id']

        if not idMarker:
            return jsonify( { 'error': 'Нет ID' } )

        user = oauth.fetch_user()

        cursor.execute( 'DELETE FROM territories WHERE id = ' + idMarker + ' AND user = "' + str(user.id) + '"' )  
        conn.commit()

        return jsonify({'success': 'Маркер удален'})

@app.route('/territories', methods=['POST', 'GET'])
@requires_authorization
def territories():
    user = oauth.fetch_user()

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM territories WHERE user = '" + str(user.id) + "'")
    markers = cursor.fetchall()

    return render_template('territories.html', user=user, auth_ok=1, markers=markers)

@app.route('/locations')
def location_markers():
    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM territories")
    markers = cursor.fetchall()

    terrs = {}

    for marker in markers:
        terrs[marker["name"]] = { 'territory': "'" + marker["name"] + "'", "guild":"", "acquired":"2021-05-05 02:24:09", "attacker":'null', "location":{"startX": marker["xStart"], "startY": marker["zStart"], "endX": marker["xStop"], "endY": marker["zStop"]} }
    
    terr = { 'territories': terrs }
    
    resp = jsonify(terr)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

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

def _is_numb ( digit ):
    return digit.isdigit() if digit[:1] != '-' else digit[1:].isdigit()

if __name__ == '__main__':
    app.run(host='0.0.0.0')
