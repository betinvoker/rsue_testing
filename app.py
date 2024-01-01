from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite///db_rsue_testing.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.current_timestamp())

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/creating_tests")
def creatingTests():
    return render_template('creating_tests.html')

@app.route("/my_tests")
def myTests():
    return render_template('my_tests.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)