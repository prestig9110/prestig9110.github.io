from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flask import escape
from flaskext.mysql import MySQL
from webargs import flaskparser, fields
import requests
import re
import os
from flask import redirect, url_for
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import discord
from pprint import pprint
from inspect import getmembers

app = Flask(__name__)
app._static_folder = 'static'

mysql = MySQL()

app.config.from_pyfile('config.py', silent=True)

mysql.init_app(app)

app.secret_key = b"random bytes representing flask secret key2"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"

oauth = DiscordOAuth2Session(app)

@app.route('/register', methods=['POST', 'GET'])
@requires_authorization
def register():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        error = None
        # form_args = {
        #     'login': fields.Str(required=True),
        #     'password': fields.Str(required=True),
        #     'tag': fields.Str(required=True),
        #     'typeMc': fields.Int(required=False),
        #     'age': fields.Int(required=False),
        #     'from_about': fields.Str(required=False),
        #     'you_about': fields.Str(required=False)
        # }

        # params = flaskparser.parser.parse(form_args, request)

        login      = request.form['login']
        password   = request.form['password']
        tag        = request.form['tag']
        typeMc     = request.form['type']
        age        = request.form['age']
        from_about = request.form['from_about']
        you_about  = request.form['you_about']
        servers    = request.form['servers']

        # print(params, flush=True)

        if not login:
            return jsonify( { 'error': 'Не указан логин' } )
        if not password:
            return jsonify( { 'error': 'Не указан пароль' } )
        if not typeMc:
            return jsonify( { 'error': 'Не указан тип аккаунта' } )
        if not age:
            return jsonify( { 'error': 'Не указан возвраст' } )

        cursor.execute("SELECT id FROM users WHERE username = %s", ( login, ))
        user_id = cursor.fetchone()

        if user_id is not None:
            return jsonify( { 'error': 'Такой пользователь уже существует' } )

        user = oauth.fetch_user()
        userJson = user.to_json()
        pprint(userJson)
        
        cursor.execute( 
            'INSERT INTO users (username, password, tag, type, age, from_about, you_about) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                ( login, password, str(userJson), typeMc, age, from_about, you_about )
        )  
        conn.commit()
        
        ticket = 'Игровой ник: ' + login + '\n'
        ticket = ticket + 'Аккаунт: ' + ('Лицензия' if type else 'Пиратка') + '\n'
        ticket = ticket + 'Ваш возраст: ' + age + '\n'
        ticket = ticket + 'Предыдущие сервера: ' + servers + '\n'
        ticket = ticket + 'Откуда узнали о проекте: ' + from_about + '\n'
        ticket = ticket + 'Интересы в Minecraft: ' + you_about

        # url = 'https://discord.com/api/webhooks/666240097955610626/nmEW5q7OtO9A1ac-37XfQ7oSi-1aGbuU_nENtmCTjmCV50XdYnwXVrT7p0k5aVAqpHRo'
        url = 'https://discord.com/api/webhooks/836649209067208735/znHwUvG2NJ2q93zFfFWfek_HJztFKCOpv4fcchPvfy2XvFhhje6sHm5pe0LsJ6t8_6CS'

        data = {
            "content" : ticket,
            "username" : 'applicant'
        }

        result = requests.post(url, json = data)

        # channel.send('Привет. Вы оставили заявку')
        # user.send('Привет. Вы оставили заявку')

        return jsonify({'success': 'Вы успешно зарегистрировались'})
    
    return jsonify({'error': 'При регистрации произошка ошибка'})

@app.route('/')
def index():
    auth_ok = 0
    user = {}

    if oauth.authorized:
        auth_ok = 1
        user = oauth.fetch_user()

    return render_template('Index.html', user=user, auth_ok=auth_ok)

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

    guilds = oauth.request('/users/@me/guilds')

    pprint(getmembers(guilds))

    gmg_ok = 0

    for guild in guilds:
        if guild['id'] == '723912565234728972':
            gmg_ok = 1

    return render_template('me.html', gmg_ok=gmg_ok, user=user, auth_ok=1)

if __name__ == '__main__':
    app.run(debug=True)
