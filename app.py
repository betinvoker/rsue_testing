from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db_rsue_testing.db"
db = SQLAlchemy(app)

#   Cущности базы данных
#   Класс Пользователь 
class User(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    login = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(1), unique=False, nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.current_timestamp())

#   Класс Группа
class Group(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=False, nullable=False)
    course = db.Column(db.String(1), unique=False, nullable=False)
    year_study = db.Column(db.String(4), unique=False, nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.current_timestamp())

#   Класс связи Пользователь-Группа (Многие ко многим)
class UserGroup(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_user = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    id_group = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.current_timestamp())

@app.route("/")
def index():
    tests = Group.query.all()
    return render_template('index.html', tests=tests)

@app.route("/creating_tests")
def creatingTests():
    return render_template('creating_tests.html')

@app.route("/my_tests")
def myTests():
    return render_template('my_tests.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)