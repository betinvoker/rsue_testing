from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///db_rsue_testing.db"
app.config['SECRET_KEY'] = "842de5e701cefac628e04455cd3102391d0ba226"
db = SQLAlchemy(app)

#   Cущности базы данных
#   Класс Пользователь 
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    login = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(1), unique=False, nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

#   Класс Группа
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), unique=False, nullable=False)
    course = db.Column(db.String(1), unique=False, nullable=False)
    year_study = db.Column(db.String(4), unique=False, nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

#   Класс связи Пользователь-Группа (Многие ко многим)
class UserGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_user = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    id_group = db.Column(db.BigInteger, db.ForeignKey('group.id'), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

#   Класс Тест
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(1000), unique=False, nullable=False)
    description = db.Column(db.Text(), unique=False, nullable=True)
    id_author = db.Column(db.BigInteger, db.ForeignKey('user.id'), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

#   Класс Вопросы к тесту
class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text(), unique=False, nullable=False)
    count_responses = db.Column(db.String(1), unique=False, default=db.func.text('1'))
    id_test = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

#   Класс Ответы к вопросу
class Response(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    response = db.Column(db.Text(), unique=False, nullable=False)
    count_point = db.Column(db.Integer, unique=False, default=db.func.text('0'))
    id_quest = db.Column(db.Integer, db.ForeignKey('quest.id'), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())

#   Класс Ответы пользователей
class Result_testing(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_test = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=False)
    id_quest = db.Column(db.Integer, db.ForeignKey('quest.id'), nullable=False)
    id_response = db.Column(db.Integer, db.ForeignKey('response.id'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    create_date = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    update_date = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())


@app.route("/", methods=['POST','GET'])
def index():
    dictUserLogin, dictCountQuests = {},{}

    if request.method == 'POST' and 'tests_search' in request.form:
        tests_search = request.form['tests_search']
        search = "%{}%".format(tests_search)
        tests = Test.query.filter(Test.name.like(search)).all()

        for test in tests:
            count_quest = Quest.query.filter_by(id_test=test.id).count()
            user = User.query.get(test.id_author).login

            dictUserLogin.setdefault(test.id, user)
            dictCountQuests.setdefault(test.id, count_quest)

        return render_template('index.html', tests=tests, users=dictUserLogin, count_quests=dictCountQuests, tests_search=tests_search)

    else:
        tests = Test.query.order_by(Test.create_date.desc()).limit(100).all()
    
        for test in tests:
            count_quest = Quest.query.filter_by(id_test=test.id).count()
            user = User.query.get(test.id_author).login

            dictUserLogin.setdefault(test.id, user)
            dictCountQuests.setdefault(test.id, count_quest)

        return render_template('index.html', tests=tests, users=dictUserLogin, count_quests=dictCountQuests)

@app.route("/creating_test", methods=['POST','GET'])
def creatingTest():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        test = Test(name=name, description=description, id_author=1, update_date=datetime(3000, 1, 1, 00, 00, 00))

        try:
            db.session.add(test)
            db.session.commit()

            return redirect('/my_tests')
        except:
            return 'Произошла ошибка. Данные не добавлены!'
    else:
        return render_template('creating_test.html')

@app.route("/my_tests")
def myTests():
    user = User.query.get(1)
    tests = Test.query.filter_by(id_author=user.id).order_by(Test.create_date.desc()).all()
    quests = db.session.query(
        Quest.id,
        Quest.question,
        Quest.count_responses,
        Quest.id_test,
        Quest.create_date).join(Test, Quest.id_test == Test.id).all()
    
    dictCountResponses = {}
    for quest in quests:
        count_responses = Response.query.filter_by(id_quest=quest.id).count()
        dictCountResponses.setdefault(quest.id, count_responses)

    return render_template('my_tests.html', tests=tests, quests=quests, responses=dictCountResponses)

@app.route("/quest_create/<int:id>", methods=['POST','GET'])
def questCreate(id):
    if request.method == 'POST':
        question = request.form['question']
        count_responses = request.form['count_responses']
        quest = Quest(question=question, count_responses=count_responses, id_test=id, update_date=datetime(3000, 1, 1, 00, 00, 00))
        
        try:
            db.session.add(quest)
            db.session.commit()
            return redirect('/my_tests')
        except:
            return 'Произошла ошибка. Данные не добавлены!' 
    else:
        return render_template('quest_create.html')
    
@app.route("/quest_update/<int:id>", methods=['POST','GET'])
def questUpdate(id):
    quest = Quest.query.get_or_404(id)
    test = Test.query.filter_by(id=quest.id_test).first()

    if request.method == 'POST':
        question = request.form['question']
        count_responses = request.form['count_responses']
        
        try:
            quest.question = question
            quest.count_responses = count_responses
            db.session.commit()
            return redirect('/my_tests')
        except:
            return 'Произошла ошибка. Данные не изменены!' 
    else:
        return render_template('quest_update.html', test=test, quest=quest)

@app.route("/quest_delete/<int:id>")
def questDelete(id):
    quest = Quest.query.get_or_404(id)
    
    try:
        db.session.delete(quest)
        db.session.commit()
        return redirect('/my_tests')
    except:
        return "При удалении записи произошла ошибка!"

@app.route("/create_response/<int:id>", methods=['POST','GET'])
def responseCreate(id):
    quest = Quest.query.get_or_404(id)
    responses = Response.query.filter_by(id_quest=id).order_by(db.desc(Response.create_date)).all()
    
    sum_pounts = 0
    for response in responses:
        sum_pounts += response.count_point

    if request.method == 'POST':
        print(request.form['response'], request.form['count_point'])
        response = request.form['response']
        count_point = request.form['count_point']

        date = Response(response=response, count_point=count_point, id_quest=id, update_date=datetime(3000, 1, 1, 00, 00, 00))
        
        try:
            db.session.add(date)
            db.session.commit()
            return redirect('/my_tests')
        except:
            return 'Произошла ошибка. Данные не добавлены!' 
    else:
        return render_template('create_response.html', quest=quest, responses=responses, sum_pounts = sum_pounts)
    
@app.route("/update_response/<int:id>", methods=['POST','GET'])
def responseUpdate(id):
    resp = Response.query.get_or_404(id)
    quest = Quest.query.filter_by(id=resp.id_quest)
    responses = Response.query.filter_by(id_quest=id).order_by(db.desc(Response.create_date)).all()
    
    sum_pounts = 0
    for response in responses:
        sum_pounts += response.count_point

    if request.method == 'POST':
        response = request.form['response']
        count_point = request.form['count_point']
        
        try:
            resp.response = response
            resp.count_point = count_point
            db.session.commit()
            return redirect('/my_tests')
        except:
            return 'Произошла ошибка. Данные не изменены!' 
    else:
        return render_template('update_response.html', quest=quest, resp=resp, responses=responses, sum_pounts = sum_pounts)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)