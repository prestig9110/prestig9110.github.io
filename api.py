from flask import Blueprint, request, jsonify, g
from decorators import bearer_required
from registration import create_user
import re
from hello import app, get_db
import json

api = Blueprint('api', __name__, template_folder='templates')

@api.route("/api/create_user/", methods=['POST', 'GET'])
@bearer_required
def api_create_user():
    if request.method == 'POST':

        try:
            reqJson = request.get_json()
        except:
            return jsonify( { "error": "json invalid", "status_code": 400, "success": "" } ), 400

        if reqJson is None:
            return jsonify( { "error": "json invalid or Content-Type", "status_code": 400, "success": "" } ), 400

        fields = dict({'login': '', 'password': '', 'type': '', 'age': '', 'from_about': '', 'you_about': '', 'servers': '', 'user_json': ''})

        for key in fields.keys():
            if key == 'servers':
                if key in reqJson:
                    fields[key] = reqJson[key]
                else:
                    fields[key] = ''

            if key in reqJson:
                fields[key] = reqJson[key]
            else:
                return jsonify( { "error": key + " invalid or does not exist", "status_code": 400, "success": "" } ), 400

        # if 'login' in reqJson:
        #     login      = reqJson['login']
        # else:
        #     return jsonify( { "error": "login invalid or does not exist", "status_code": 400, "success": "" } ), 400
        # password   = reqJson['password']
        # typeMc     = reqJson['type']
        # age        = str(reqJson['age'])
        # from_about = reqJson['from_about']
        # you_about  = reqJson['you_about']
        # servers    = reqJson['servers']
        # userJson   = reqJson['user_json']

        fields['typeMc'] = fields['type']
        fields['userJson'] = fields['user_json']

        if not fields['login'] or re.search("\s|@", fields['login']):
            return jsonify( { "error": "login not specified or invalid", "status_code": 400, "success": "" } ), 400
        if not fields['password'] or re.search("\s", fields['password']):
            return jsonify( { "error": "password not specified or invalid", "status_code": 400, "success": "" } ), 400
        if not fields['typeMc']:
            return jsonify( { "error": "account type not specified", "status_code": 400, "success": "" } ), 400
        if not fields['age'] or not re.match("\d+$", str(fields['age'])):
            return jsonify( { "error": "age not specified or specified incorrectly", "status_code": 400, "success": "" } ), 400
        if len(fields['password']) < 8:
            return jsonify( { "error": "password must be at least 8 characters", "status_code": 400, "success": "" } ), 400
        if not fields['from_about'] or not re.search("\w", fields['from_about']):
            return jsonify( { "error": "from_about empty", "status_code": 400, "success": "" } ), 400
        if not fields['you_about'] or not re.search("\w", fields['you_about']):
            return jsonify( { "error": "you_about empty", "status_code": 400, "success": "" } ), 400
        if not fields['userJson']:
            return jsonify( { "error": "user_json invalid", "status_code": 400, "success": "" } ), 400

        bearer = request.headers['Authorization'].encode('ascii','ignore')
        token = str.replace(str(bearer), 'Bearer ','')

        if token != app.config["BEARER_SUPERHUB"]:
            fields['partner'] = "superhub"

        response = create_user(fields)
            # login = login, password = password, typeMc = typeMc, age = age, from_about = from_about, you_about = you_about, servers = servers, partner = partner, userJson = userJson
        # )

        if response == "exist user":
            return jsonify( { "error": "this user already exists", "status_code": 400, "success": "" } ), 400
        
        if response == "ok":
            return jsonify({"success": "registration successful", "status_code": 200, "error": "" } ), 200

        return jsonify( { "error": "unknown error", "status_code": 400, "success": "" } ), 400

@api.route("/api/get_status/", methods=['POST', 'GET'])
@bearer_required
def api_get_status():
    if request.method == 'POST':

        try:
            reqJson = request.get_json()
        except:
            return jsonify( { "error": "json invalid", "status_code": 400, "status": None } ), 400

        user_id = reqJson['user_id']

        get_db()

        g.cursor.execute("SELECT status FROM users WHERE user_id = %s", ( str(user_id) ))
        user_id = g.cursor.fetchone()

        if user_id is None:
            return jsonify( { "error": "user is not found", "status_code": 400, "status": None } ), 400
        else:
            return jsonify( { "error": "", "status_code": 200, "status": user_id["status"] } ), 200

        return jsonify( { "error": "unknown error", "status_code": 400, "status": None } ), 400

