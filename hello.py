from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify
from flaskext.mysql import MySQL

app = Flask(__name__)

mysql = MySQL()

app.config.from_pyfile('config.py', silent=True)

mysql.init_app(app)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        conn = mysql.connect()
        cursor =conn.cursor()

        # cursor.execute("SELECT * from User")
        # data = cursor.fetchone()

        return jsonify({'success': app.config['MYSQL_DATABASE_USER'] + ' вы успешно зарегистрировались'})
    
    return jsonify({'error': 'При регистрации произошка ошибка'})

@app.route('/')
def index():
    return render_template('Index.html')