from flask import Blueprint, g
from hello import get_db, defaultParams, app
import requests
import json

def create_user(params):
    get_db()

    if "userJson" in params and params["userJson"] is not None:
        userJson = params["userJson"]
        userId = str(userJson["id"])
    else:
        defaultParams()
        userJson = g.user.to_json()
        userId = str(g.user.id)

    g.cursor.execute("SELECT id FROM users WHERE user_id = %s OR username = %s", ( str(userId), params["login"] ))
    user_id = g.cursor.fetchone()

    if user_id is not None:
        return "exist user"

    print(params)

    g.cursor.execute( 
        'INSERT INTO users (username, password, tag, type, age, from_about, you_about, status, user_id, partner) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
            ( params["login"], params["password"], str(userJson), params["typeMc"], params["age"], 
              params["from_about"], params["you_about"], 1, str(userJson['id']), params["partner"] )
    )  
    g.conn.commit()
    
    ticket = 'Игровой ник: ' + params["login"] + '\n'
    ticket = ticket + 'Аккаунт: ' + ('Лицензия' if params["typeMc"] == '1' else 'Пиратка') + '\n'
    ticket = ticket + 'Ваш возраст: ' + str(params["age"]) + '\n'
    ticket = ticket + 'Предыдущие сервера: ' + params["servers"] + '\n'
    ticket = ticket + 'Откуда узнали о проекте: ' + params["from_about"] + '\n'
    ticket = ticket + 'Интересы в Minecraft: ' + params["you_about"] + '\n'
    ticket = ticket + 'Заявка от: ' + params["partner"] + '\n'
    if "username" in userJson and "discriminator" in userJson:
        ticket = ticket + 'Дискорд тэг: ' + str(userJson['username']) + '#' + str(userJson['discriminator']) + '\n'
    else: 
        ticket = ticket + 'Дискорд тэг: ' + str(userJson['id']) + '\n'

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

    return "ok"