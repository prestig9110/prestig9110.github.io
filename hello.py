from flask import Flask
from flask import render_template
from flask import request
from flask import jsonify

app = Flask(__name__)

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        return jsonify({'success': request.form['name'] + ' вы успешно зарегистрировались'})
    
    return jsonify({'error': 'При регистрации произошка ошибка'})

@app.route('/')
def index():
    return render_template('Index.html')