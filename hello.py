from flask import Flask, redirect, url_for, render_template, request, jsonify, escape, flash
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import requests
import os
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
from pprint import pprint
from inspect import getmembers
import json
import pika
from flask_caching import Cache
import re
import random
import hashlib
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app._static_folder = 'static'

mysql = MySQL()

app.config.from_pyfile('config.py', silent=True)

mysql = MySQL(cursorclass=DictCursor, init_command='SET NAMES utf8mb4')
mysql.init_app(app)

app.secret_key = b"random bytes representing flask secret key2"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = app.config["DEV"]

oauth = DiscordOAuth2Session(app)

config = {
    "DEBUG": False,          
    "CACHE_TYPE": "redis",
    "CACHE_DEFAULT_TIMEOUT": 300,
    'CACHE_REDIS_URL': 'redis://127.0.0.1:6379/'
}

app.config.from_mapping(config)

cache = Cache(app)

# global jwt_token
# global jwt_refresh_token

def get_token(refresh):
    if refresh:
        pprint(refresh)

        # headers = 'Authorization' : "'" + Bearer + " " + jwt_refresh_token + "'"

        try:
            result = requests.post(
                app.config["JWT_URL"] + 'refresh', 
                data = {}, 
                headers = { 'Authorization' : 'Bearer ' + jwt_refresh_token }
            )
        except:
            return 'error_'

        if result.status_code == 401:
            get_token(refresh=0)
        
        tokens = result.json()

        pprint(tokens['access_token'])

        return tokens['access_token']
    else:
        data = {
            "username" : app.config["JWT_LOGIN"],
            "password" : app.config["JWT_PASS"]
        }

        try:
            result = requests.post(app.config["JWT_URL"] + 'login', json = data)
        except:
            return 'error_', 'error_'

        tokens = result.json()
        
        return tokens['access_token'], tokens['refresh_token']

jwt_token, jwt_refresh_token = get_token(refresh=0)
#jwt_token = get_token(refresh=1)

# pprint(jwt_token)

def defaultParams():
    auth_ok = 0
    user = {}

    if oauth.authorized:
        auth_ok = 1
        user = oauth.fetch_user()

    resposeCache = cache.get('responseCategory')

    if resposeCache is None:
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM category')
        resposeCache = cursor.fetchall()

        cache.set('responseCategory', resposeCache, timeout=10800)

    return {'user': user, 'auth_ok': auth_ok, 'categories': resposeCache}

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

        if not login or re.search("\s|@", login):
            return jsonify( { 'error': 'Не указан или не корректный логин' } )
        if not password or re.search("\s", password):
            return jsonify( { 'error': 'Не указан или не корректный пароль' } )
        if not typeMc:
            return jsonify( { 'error': 'Не указан тип аккаунта' } )
        if not age or not re.match("\d+$", age):
            return jsonify( { 'error': 'Не указан или указан не корректно возвраст' } )
        if len(password) < 8:
            return jsonify( { 'error': 'Пароль должен быть минимум из 8 символов' } )
        if not from_about or not re.search("\w", from_about):
            return jsonify( { 'error': 'Расскажите о себе, пожалуйста' } )
        if not you_about or not re.search("\w", you_about):
            return jsonify( { 'error': 'Расскажите о себе, пожалуйста' } )

        user = oauth.fetch_user()
        userJson = user.to_json()

        cursor.execute("SELECT id FROM users WHERE user_id = %s OR username = %s", ( str(user.id), login ))
        user_id = cursor.fetchone()

        if user_id is not None:
            return jsonify( { 'error': 'Такой пользователь уже существует' } )

        cursor.execute( 
            'INSERT INTO users (username, password, tag, type, age, from_about, you_about, status, user_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', 
                ( login, password, str(userJson), typeMc, age, from_about, you_about, 1, str(userJson['id']) )
        )  
        conn.commit()
        
        ticket = 'Игровой ник: ' + login + '\n'
        ticket = ticket + 'Аккаунт: ' + ('Лицензия' if typeMc == '1' else 'Пиратка') + '\n'
        ticket = ticket + 'Ваш возраст: ' + age + '\n'
        ticket = ticket + 'Предыдущие сервера: ' + servers + '\n'
        ticket = ticket + 'Откуда узнали о проекте: ' + from_about + '\n'
        ticket = ticket + 'Интересы в Minecraft: ' + you_about + '\n'
        ticket = ticket + 'Дискорд тэг: ' + userJson['username'] + '#' + userJson['discriminator'] + '\n'

        if app.config["DEV"] == "true":
            ticket = ticket + "\nЭто тестовая заявка"

        data = {
            "content" : "```" + ticket + "```" + '<@' + userJson['id'] + '>',
            "username" : 'applicant',
            "allowed_mentions": {
                "parse": ["users"],
                "users": []
            }
        }

        result = requests.post(app.config["WEBHOOKURL"], json = data)

        return jsonify({'success': 'Вы успешно зарегистрировались'})
    
    return jsonify({'error': 'При регистрации произошка ошибка'})

@app.route('/')
def index():
    return render_template(
        'index.html', 
        params = defaultParams(),
        version = app.config["GAME_VERSION"]
    )

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
    params = defaultParams()
    user = params["user"]

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

    return render_template(
        'profile/me.html', 
        params  = params,
        gmg_ok  = gmg_ok,  
        user_id = user_id, 
        users   = users, 
        markers = markers, 
        opUser  = opUser,
        version = app.config["GAME_VERSION"]
    )

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
            where = ' AND user = "' + str(user.id) + '"'

            if str(user.id) in app.config["PERMISSIONS"]:
                where = ''

            cursor.execute( 
                'UPDATE markers SET id_type = %s, x = %s, y = %s, z = %s, name = %s, description = %s, server = %s, flag = %s WHERE id = %s' + where,
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
@requires_authorization
def other_markers():
    params = defaultParams()

    if not str(params["user"].id) in app.config["PERMISSIONS"]:
        return 'Доступ запрещен'

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT markers.*, username FROM markers join users on user = user_id order by username")
    markers = cursor.fetchall()

    return render_template('other_markers.html', params = params, markers=markers, opUser=1)

@app.route("/farm_manager", methods=['POST', 'GET'])
@requires_authorization
def farm_manager():
    params = defaultParams()

    if not str(params["user"].id) in app.config["PERMISSIONS"]:
        return 'Доступ запрещен'

    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form['action']

        if action == 'add' or action == 'edit':
            server = request.form['server']
            name   = request.form['name']
            x      = request.form['x']
            y      = request.form['y']
            z      = request.form['z']

            if action == 'add':
                cursor.execute( 
                    'INSERT INTO farm_manager (x, y, z, name, server) VALUES (%s, %s, %s, %s, %s)', 
                        ( x, y, z, name, server)
                )

                conn.commit()

                return jsonify({'success': cursor.lastrowid})

            if action == 'edit':
                markerID = request.form['markerID']

                cursor.execute( 
                    'UPDATE farm_manager SET x = %s, y = %s, z = %s, name = %s, server = %s WHERE id = %s',
                        ( x, y, z, name, server, markerID )
                )

                conn.commit()

                return jsonify({'success': int(markerID)})
        
        if action == 'del':
            idMarker = request.form['id']

            cursor.execute( 'DELETE FROM farm_manager WHERE id = ' + idMarker )  
            conn.commit()

            return jsonify({'success': 'Ферма удалена'})

        if action == 'reinit':
            cursor.execute("SELECT * FROM farm_manager")
            farms = cursor.fetchall()

            data = {"farm": dict(), "main": dict()}

            for farm in farms:
                key = ",".join((str(farm["x"]),str(farm["y"]),str(farm["z"])))

                if farm["server"] == 'gmgame':
                    data["main"].update({key: farm["name"]})
                else:
                    data["farm"].update({key: farm["name"]})
		
                signX = str(farm["x"])[:1]
                signZ = str(farm["z"])[:1]

                x = int(str(farm["x"])[1:] if signX == '-' else farm["x"])
                z = int(str(farm["z"])[1:] if signZ == '-' else farm["z"])

                addXpositive = [ signX + str(i) if signX == '-' else str(i) for i in range(x, x+6, 1)]
                addXnegative = [ signX + str(i) if signX == '-' else str(i) for i in range(x-6, x, 1)]
                addZpositive = [ signZ + str(i) if signZ == '-' else str(i) for i in range(z, z+6, 1)]
                addZnegative = [ signZ + str(i) if signZ == '-' else str(i) for i in range(z-6, z, 1)]

                for i in range(0,5):
                    keyPositiveX = addXpositive[i] 
                    keyNegativeX = addXnegative[i]
                    for i in range(0,5):
                        keyPositive = ",".join((keyPositiveX,str(farm["y"]),addZpositive[i]))
                        keyPositiveNegative = ",".join((keyPositiveX,str(farm["y"]),addZnegative[i]))
                        keyNegative = ",".join((keyNegativeX,str(farm["y"]),addZnegative[i]))
                        keyNegativePositive = ",".join((keyNegativeX,str(farm["y"]),addZpositive[i]))

                        if farm["server"] == 'gmgame':
                            data["main"].update({keyPositive: farm["name"]})
                            data["main"].update({keyPositiveNegative: farm["name"]})
                            data["main"].update({keyNegative: farm["name"]})
                            data["main"].update({keyNegativePositive: farm["name"]})
                        else:
                            data["farm"].update({keyPositive: farm["name"]})
                            data["farm"].update({keyPositiveNegative: farm["name"]})
                            data["farm"].update({keyNegative: farm["name"]})
                            data["farm"].update({keyNegativePositive: farm["name"]})

            response = _sendRequest('reinitFarmManager', data)

            if 'error' in response:
                return jsonify( { 'error': 'Не удалось перезапустить' } )


            if 'ok' in response:
                return jsonify( { 'ok': 'Перезапущено' } )          

    cursor.execute("SELECT * FROM farm_manager")
    farms = cursor.fetchall()

    return render_template('farm_manager.html', params = params, farms=farms, opUser=1)

@app.route("/list_players/", methods=['POST', 'GET'])
@requires_authorization
def list_players():
    params = defaultParams()

    if not str(params["user"].id) in app.config["PERMISSIONS"]:
        return 'Доступ запрещен'

    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':
        id_group = request.form['id']

        cursor.execute("SELECT id, username, age, status, tag FROM users WHERE status = " + str(id_group) + " ORDER BY status")
    else:
        cursor.execute("SELECT id, username, age, status, tag FROM users WHERE status = 1 ORDER BY status")

    users = cursor.fetchall()

    usersResult = {}
    for item in users:
        tag = json.loads(re.sub('[^A-Za-z0-9{}\':,@._-]+', '', item["tag"]).replace("'",'"').replace("True", "true").replace("False", "false").replace("None", "null"))
        item["email"] = tag["email"]
        if item['status'] in usersResult:
            usersResult[item["status"]].append(item)
        else:
            usersResult[item['status']] = [item]

    if request.method == 'POST':
        return jsonify({'usersResult': usersResult})

    return render_template('list_players.html', params = params, usersResult = usersResult)

@app.route('/change_user', methods=['POST', 'GET'])
@requires_authorization
def change_user():
    if app.config["DEV"] == "true":
        return jsonify( { 'message': 'Статус изменен' } )

    user = oauth.fetch_user()

    if not str(user.id) in app.config["PERMISSIONS"]:
        return 'Отказано в доступе'

    userID = request.form['id']
    action = request.form['action']
    username = request.form['username']

    if not userID or not action:
        return jsonify( { 'message': 'Нет обязательного параметра' } )

    status = 1

    conn = mysql.connect()
    cursor = conn.cursor()

    if action == 'accept':
        if not username:
            return jsonify( { 'message': 'Нет обязательного параметра' } )

        status = 2

        cursor.execute("SELECT password, type FROM users WHERE id = %s", ( str(userID) ))
        password = cursor.fetchone()

        data = {
            "username" : username,
            "password" : password['password'],
            "type" : password['type']
        }

        response = _sendRequest('add_user', data)

        if 'error' in response:
            return jsonify( { 'error': 'Не удалось добавить' } )
    
    elif action == 'del_wl':
        if not username:
            return jsonify( { 'message': 'Нет обязательного параметра' } )

        status = 5

        data = {
            "username" : username
        }

        response = _sendRequest('del_wl', data)

        if 'error' in response:
            return jsonify( { 'error': 'Не удалось удалить' } )
    
    elif action == 'add_wl':
        if not username:
            return jsonify( { 'message': 'Нет обязательного параметра' } )

        status = 2

        data = {
            "username" : username
        }

        response = _sendRequest('add_wl', data)

        if 'error' in response:
            return jsonify( { 'error': 'Не удалось добавить' } )

    elif action == 'not_accept' or action == 'unban':
        status = 3
    elif action == 'ban':
        if not username:
            return jsonify( { 'message': 'Нет обязательного параметра' } )

        status = 4

        data = {
            "username" : username
        }

        response = _sendRequest('del_wl', data)

        if 'error' in response:
            return jsonify( { 'error': 'Не удалось забанить' } )
    elif action == 'delete':
        if not username:
            return jsonify( { 'message': 'Нет обязательного параметра' } )

        data = {
            "username" : username
        }

        response = _sendRequest('del_wl', data)

        if 'error' in response:
            return jsonify( { 'error': 'Не удалось удалить' } )

        cursor.execute( "DELETE FROM users WHERE id = %s", (userID) )
        conn.commit()

        return jsonify( { 'message': 'Заявка удалена' } )

    cursor.execute( "UPDATE users SET status = %s WHERE id = %s", (status, userID) )
    conn.commit()

    return jsonify( { 'message': 'Статус изменен' } )


@app.route('/add_territories', methods=['POST', 'GET'])
@requires_authorization
def add_territories():
    if request.method == 'POST':
        conn   = mysql.connect()
        cursor = conn.cursor()
        error  = None

        name   = request.form['name']
        xStart = request.form['xStart']
        zStart = request.form['zStart']
        xStop  = request.form['xStop']
        zStop  = request.form['zStop']
        world  = request.form['world']

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
            where = ' AND user = "' + str(user.id) + '"'

            if str(user.id) in app.config["PERMISSIONS"]:
                where = ''

            cursor.execute( 
                'UPDATE territories SET xStart = %s, zStart = %s, xStop = %s, name = %s, zStop = %s, world = %s WHERE id = %s' + where,
                    ( xStart, zStart, xStop, name, zStop, world, markerID )
            )  
        else:
            cursor.execute("SELECT id FROM territories WHERE name = %s", ( name ) )
            terr = cursor.fetchone()

            if terr is not None:
                return jsonify( { 'error': 'Такая метка уже существует' } )

            cursor.execute( 
                'INSERT INTO territories (xStart, zStart, xStop, zStop, name, user, world) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                    ( xStart, zStart, xStop, zStop, name, str(user.id), world)
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

        where = ' AND user = "' + str(user.id) + '"'

        if str(user.id) in app.config["PERMISSIONS"]:
            where = ''

        cursor.execute( 'DELETE FROM territories WHERE id = ' + idMarker + where )  
        conn.commit()

        return jsonify({'success': 'Маркер удален'})

@app.route("/other_territories/")
@requires_authorization
def other_territories():
    params = defaultParams()

    if not str(params["user"].id) in app.config["PERMISSIONS"]:
        return 'Доступ запрещен'

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM territories join users on user = user_id order by username")
    territories = cursor.fetchall()

    return render_template('other_territories.html', params = params, markers=territories, opUser=1)

@app.route('/territories', methods=['POST', 'GET'])
@requires_authorization
def territories():
    params = defaultParams()

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM territories WHERE user = '" + str(params["user"].id) + "'")
    markers = cursor.fetchall()

    return render_template('territories.html', params = params, markers=markers)

@app.route('/locations/<world>')
def location_markers(world):
    terrs = cache.get('responseLocation_' + world)

    if terrs is None:
        conn = mysql.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM territories WHERE world = '" + world + "'")
        markers = cursor.fetchall()

        terrs = {}

        for marker in markers:
            terrs[marker["name"]] = { 
                'territory': "'" + marker["name"] + "'", 
                "guild":"", 
                "acquired":"2021-05-05 02:24:09", 
                "attacker":'null', 
                "location":{
                    "startX": marker["xStart"], 
                    "startY": marker["zStart"], 
                    "endX": marker["xStop"], 
                    "endY": marker["zStop"]
                } 
            }
        
        cache.set('responseLocation_' + world, terrs, timeout=600)
        
    terr = { 'territories': terrs, 'world': world }
        
    resp = jsonify(terr)

    resp.headers['Access-Control-Allow-Origin'] = '*'

    return resp

@app.route('/change_password', methods=['POST', 'GET'])
@requires_authorization
def change_password():
    params = defaultParams()

    if request.method == 'POST':

        password = request.form['password']

        if not password:
            return jsonify( { 'error': 'Не указан пароль' } )
        if len(password) < 8:
            return jsonify( { 'error': 'Пароль должен быть минимум из 8 символов' } )
        if len(password) > 15:
            return jsonify( { 'error': 'Пароль должен быть максимум из 15 символов' } )

        conn = mysql.connect()
        cursor = conn.cursor()

        # cursor.execute( 
        #     'UPDATE users SET password = %s WHERE user_id = %s', ( password, str(user.id) )
        # )

        # conn.commit

        cursor.execute("SELECT username FROM users WHERE user_id = %s", ( str(params["user"].id) ))
        username = cursor.fetchone()

        if username is None:
            return jsonify( { 'error': 'Нет такого имени' } )

        data = {
            "password" : password,
            "login" : username['username']
        }

        response = _sendRequest('change_password', data)

        if 'error' in response:
            return jsonify( { 'error': 'Не удалось изменить пароль' } )


        if 'ok' in response:
            return jsonify( { 'ok': 'Пароль изменен' } )
    #     return response

        # credentials = pika.PlainCredentials(app.config["MQ_USER"], app.config["MQ_PASS"])
        # connection = pika.BlockingConnection(pika.ConnectionParameters(host=app.config["MQ_HOST"], credentials=credentials))
        # channel = connection.channel()
        # properties = pika.BasicProperties(delivery_mode = 2);

        # channel.queue_declare(queue='tasks', durable=True)

        # channel.basic_publish(
        #     exchange='',
        #     properties=properties,
        #     routing_key='tasks',
        #     body=json.dumps( { "task" : "change_password", "user" : str(user.id) } )
        # )
        # connection.close()

        # return jsonify({'ok': 'Пароль будет изменен в ближайшее время'})

    return render_template('change_password.html', params = params)

def _sendRequest(url, data):
    global jwt_token

    try:
        response = requests.post(
            app.config["JWT_URL"] + url, 
            json = data, 
            headers = { 'Authorization' : 'Bearer ' + jwt_token }
        )
    except:
        return jsonify({'error': 'Какие то неполадки, попробуйте, пожалуйста, позже'})

    if response.status_code == 401:
        jwt_token = get_token(refresh=1)

        return _sendRequest(url, data)

    return response.json()

@app.route("/logout")
@requires_authorization
def logout():
    oauth.revoke()
    return redirect(url_for("index"))

@app.route("/getStats")
# @cache.cached(timeout=10800)
def stats():
    # if app.config["DEV"] == "true":
    #     return jsonify({'data': [
    #         {"name": "*minemax34700", "active_playtime": "675665554", "deaths": "1", "mobs": "0", "broken": "300", "supplied": "237867254"}, 
    #         {"name": "xFothis", "active_playtime": "158113", "deaths": "0", "mobs": "0"}, 
    #         {"name": "Mabotlz", "active_playtime": "153849", "deaths": "0", "mobs": "0"}, 
    #         {"name": "Spibble", "active_playtime": "150592", "deaths": "0", "mobs": "0"}, 
    #         {"name": "*OrangeNebula699", "active_playtime": "147768", "deaths": "0", "mobs": "0"}, 
    #         {"name": "*Dannylpro", "active_playtime": "144836", "deaths": "0", "mobs": "0"}, 
    #         {"name": "xFothis", "active_playtime": "158113", "deaths": "0", "mobs": "0"}, 
    #         {"name": "Mabotlz", "active_playtime": "153849", "deaths": "0", "mobs": "0"}
    #     ]})
    resposeCache = cache.get('responseStats')

    if resposeCache is None:
        resposeCache = _sendRequest('getStats', {})
        cache.set('responseStats', resposeCache, timeout=10800)

    # response = _sendRequest('getStats', {})

    return jsonify({'data': resposeCache})

@app.route('/vote_handler', methods=['POST', 'GET'])
def vote_handler():
    if (request.form['nick'] and request.form['time'] and request.form['sign']):
        if (request.form['sign'] != hashlib.sha1((request.form['nick'] + request.form['time'] + str(app.config["SECRET_KEY_FOR_VOTE"])).encode('utf-8')).hexdigest()):
            return 'Переданные данные не прошли проверку.'
    else:
        return 'Не переданы необходимые данные.'

    chance_money = False
    chance_tools = False
    prize = ''

    if random.random() < app.config["CHANCE_MONEY"]:
        chance_money = True
        prize = "money"

    if random.random() < app.config["CHANCE_TOOLS"]:
        chance_tools = True
        prize = "tools"


    data = {
        "prize" : prize,
        "nick" : request.form['nick']
    }

    resp = _sendRequest('casino', data)

    content = request.form['nick'] + ", " + random.choice(app.config["MESSAGES_FOR_VOTE"]) + "!\n\
Cпасибо за голос на https://hotmc.ru/minecraft-server-205185\n\
Твоя поддержка очень важна для нас.\n\
Также можете принять участие в розыгрыше <https://hotmc.ru/casino-205185>\n\
Поддержать проект другим способом <https://gmgame.ru/support/>"

    if chance_money:
        content = content + "\nПоздравляю, ты выиграл 10 монет на сервере"


    if chance_tools:
        content = content + "\nПоздравляю, ты выиграл инструмент на сервере"

    data = {
        "content" : content,
        "username" : 'vote'
    }

    print (data)

    result = requests.post(app.config["WEBHOOKURL_FOR_VOTE"], json = data)

    return 'ok'

@app.route('/save_images', methods=['POST'])
@requires_authorization
def save_images():
    user = oauth.fetch_user()

    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return jsonify( { 'status': 'Файл поврежден' } )

        file = request.files['file']

        if file.filename == '':
            flash('No image selected for uploading')
            return jsonify( { 'status': 'Нет имени файла' } )

        if file and _allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pathToSave = os.path.join(app.config['UPLOAD_FOLDER'], str(user.id))

            if not os.path.isdir(pathToSave):
                os.makedirs(pathToSave)

            file.save(os.path.join(pathToSave, filename))
            print('upload_image filename: ' + filename)
            flash('Image successfully uploaded and displayed below')
            return jsonify( { "location": os.path.join('/static/users/', str(user.id), filename) } )
            # return render_template('index.html', filename=filename)
        else:
            flash('Allowed image types are - png, jpg, jpeg, gif')
            return jsonify( { 'status': 'Файл не поддерживается' } )

@app.route('/my_articles', methods=['POST', 'GET'])
@requires_authorization
def my_articles():
    params = defaultParams()

    user = params["user"]
    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':
        content = request.form['editor']
        title = request.form['title']
        category = request.form['category']

        if not content or content == '':
            return jsonify( { 'status': u'not article' } )
        if not title or title == '':
            return jsonify( { 'status': u'not title' } )
        if not category or category == '':
            return jsonify( { 'status': u'not category' } )

        prewImg = re.findall('img src="(.*?)"', content)
        img = ''

        if len(prewImg) > 0 and prewImg[0] != '':
            img = prewImg[0]
        else:
            ramdomImg = random.choice(["1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png", "10.png", "11.png", "12.png"])
            img = '/static/img/prew/' + ramdomImg

        cursor.execute( 
            'INSERT INTO articles (title, content, create_date, last_modify, user_id, category, visible, preview_img) VALUES (%s, %s, CURDATE(), CURDATE(), %s, %s, 1, %s)', 
                ( title, content, str(user.id), str(category), img )
        )  
        
        conn.commit()

    cursor.execute("SELECT * FROM articles WHERE user_id = " + str(user.id))
    articles = cursor.fetchall()

    return render_template('my_articles.html', params = params, articles=articles)

@app.route('/category/<id_category>')
def player_articles(id_category):
    params = defaultParams()

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM articles WHERE category = " + str(id_category))
    articles = cursor.fetchall()

    return render_template('player_articles.html', params = params, articles=articles)

@app.route("/article/edit/<id_article>", methods=['POST', 'GET'])
@requires_authorization
def article_edit(id_article):
    params = defaultParams()
    user = params["user"]

    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST': 
        content = request.form['editor']
        title = request.form['title']
        category = request.form['category']

        if not content or content == '':
            return jsonify( { 'status': u'not article' } )
        if not title or title == '':
            return jsonify( { 'status': u'not title' } )
        if not category or category == '':
            return jsonify( { 'status': u'not category' } )

        prewImg = re.findall('img src="(.*?)"', content)
        img = ''

        if len(prewImg) > 0 and prewImg[0] != '':
            img = prewImg[0]
        else:
            ramdomImg = random.choice(["1.png", "2.png", "3.png", "4.png", "5.png", "6.png", "7.png", "10.png", "11.png", "12.png"])
            img = '/static/img/prew/' + ramdomImg

        cursor.execute( 
            'UPDATE articles SET title = %s, content = %s, last_modify = CURDATE(), category = %s, preview_img = %s WHERE id = %s AND user_id = %s',
                ( title, content, str(category), img, id_article, str(user.id) )
        )

        conn.commit()

    cursor.execute("SELECT * FROM articles WHERE id = " + id_article + " AND user_id = " + str(user.id))
    article = cursor.fetchone()

    return render_template('article_edit.html', params = params, article=article, id_article=id_article)

@app.route("/article/<id_article>")
def article(id_article):
    params = defaultParams()

    conn = mysql.connect()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM articles WHERE id = " + id_article)
    article = cursor.fetchone()
    print(article)

    return render_template('article.html', params = params, article=article)

@app.route("/category", methods=['POST', 'GET'])
@requires_authorization
def category():
    params = defaultParams()

    if not str(params["user"].id) in app.config["PERMISSIONS"]:
        return 'Доступ запрещен'

    conn = mysql.connect()
    cursor = conn.cursor()

    if request.method == 'POST':
        action = request.form['action']

        if action == 'add':
            name_category = request.form['name_category']

            cursor.execute( 
                'INSERT INTO category (name_category) VALUES (%s)', 
                    ( name_category )
            )  
            
            conn.commit()

            return jsonify({'success': cursor.lastrowid})
        
        if action == 'edit':
            name_category = request.form['name_category']
            id = request.form['id']

            cursor.execute( 
                'UPDATE category SET name_category = %s WHERE id = %s', 
                    ( name_category, str(id) )
            )  
            
            conn.commit()

            return jsonify({'success': cursor.lastrowid})
        
        if action == 'delete':
            id = request.form['id']

            cursor.execute( 
                'DELETE FROM category WHERE id = %s', 
                    ( str(id) )
            )  
            
            conn.commit()

            return jsonify({'success': cursor.lastrowid})

    cursor.execute('SELECT * FROM category')
    categories = cursor.fetchall()

    return render_template('category.html', params=params)

@app.route("/<page>/")
def start(page):
    params = defaultParams()
    
    template = 'start.html'

    if page:
        template = page + '.html'

    try:
        return render_template(template, params = params)
    except:
        return render_template('start.html', params = params)

def _is_numb ( digit ):
    return digit.isdigit() if digit[:1] != '-' else digit[1:].isdigit()

def _allowed_file(filename):
    allowed_types = set(["png", "jpg", "jpeg", "gif"])
    print("Check if image types is allowed")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_types

if __name__ == '__main__':
    app.run(host='0.0.0.0')
