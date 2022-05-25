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

        login      = reqJson['login']
        password   = reqJson['password']
        typeMc     = reqJson['type']
        age        = str(reqJson['age'])
        from_about = reqJson['from_about']
        you_about  = reqJson['you_about']
        servers    = reqJson['servers']
        userJson   = reqJson['user_json']

        if not login or re.search("\s|@", login):
            return jsonify( { "error": "login not specified or invalid", "status_code": 400, "success": "" } ), 400
        if not password or re.search("\s", password):
            return jsonify( { "error": "password not specified or invalid", "status_code": 400, "success": "" } ), 400
        if not typeMc:
            return jsonify( { "error": "account type not specified", "status_code": 400, "success": "" } ), 400
        if not age or not re.match("\d+$", str(age)):
            return jsonify( { "error": "age not specified or specified incorrectly", "status_code": 400, "success": "" } ), 400
        if len(password) < 8:
            return jsonify( { "error": "password must be at least 8 characters", "status_code": 400, "success": "" } ), 400
        if not from_about or not re.search("\w", from_about):
            return jsonify( { "error": "from_about empty", "status_code": 400, "success": "" } ), 400
        if not you_about or not re.search("\w", you_about):
            return jsonify( { "error": "you_about empty", "status_code": 400, "success": "" } ), 400
        if not userJson:
            return jsonify( { "error": "user_json invalid", "status_code": 400, "success": "" } ), 400

        bearer = request.headers['Authorization'].encode('ascii','ignore')
        token = str.replace(str(bearer), 'Bearer ','')
        partner = ""

        if token != app.config["BEARER_SUPERHUB"]:
            partner = "superhub"

        response = create_user(
            login = login, password = password, typeMc = typeMc, age = age, from_about = from_about, you_about = you_about, servers = servers, partner = partner, userJson = userJson
        )

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

