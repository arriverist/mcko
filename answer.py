from flask import Flask, render_template, redirect, abort
from requests import get, post
from data import db_session, vocord_tickets_api
from forms.user import RegisterForm, LoginForm, SendForm, mcko_LoginForm, mcko_RegisterForm, mcko_TestForm
from data.users import User
# from forms.ticket import TicketForm
from data.tickets import Ticket
from flask_login import LoginManager, login_required
from flask_login import login_user, logout_user
import os
import json
import sqlite3
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/vocord.sqlite")
login_manager = LoginManager()
login_manager.init_app(app)
name = None
admin = False


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/add_test', methods=['GET', 'POST'])
def register_mcko():
    form = mcko_TestForm()
    return render_template("add_test.html", form=form)


@app.route('/logout')
@login_required
def logout():
    global name, admin
    logout_user()
    name, admin = None, False
    return redirect("/login_mcko")


@app.route('/main')
def main_mcko():
    global name, admin
    print([name, admin])
    if name is None:
        return redirect('/login_mcko')
    if admin:
        return render_template('teachers_main.html')
    return render_template("students_main.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.route('/to_classes')
def to_classes():
    connection = sqlite3.connect("db/2098.db")
    cursor = connection.cursor()
    classes = [["/class/" + str(el[0]), el[1]] for el in cursor.execute("SELECT * FROM classes")]
    cursor.close()
    print(classes)
    return render_template('to_classes.html', classes=classes)


@app.route('/login_mcko', methods=['GET', 'POST'])
def login_mcko():
    global name, admin
    form = mcko_LoginForm()
    if form.validate_on_submit():
        connection = sqlite3.connect("db/2098.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ? AND surname = ? AND patronymic = ? AND login = ?",
                       (form.name.data, form.surname.data, form.patronymic.data, form.login.data,))
        database_response = cursor.fetchall()
        print(database_response)
        # checking login
        if len(database_response) > 0 and form.login.data == database_response[0][-3]:
            admin = bool(int(database_response[0][-1]))
            name = form.name.data + " " + form.surname.data
            return redirect("/main")
        return render_template('login_mcko.html',
                               message="Неправильный логин", form=form, name=name)
    return render_template('login_mcko.html', title='Авторизация', form=form, name=name)


@app.route("/add_users", methods=['GET', 'POST'])
def add_users_mcko():
    global name, admin
    if name is None:
        redirect('/login_mcko')
    if not admin:
        abort(404)
    form = mcko_RegisterForm()
    if form.validate_on_submit():
        if form.secret_code.data == "lol":
            connection = sqlite3.connect('db/2098.db')
            cursor = connection.cursor()
            cursor.execute(
                'INSERT INTO users (name, surname, patronymic, login, grade, is_teacher) VALUES (?, ?, ?, ?, ?, ?)',
                (form.name.data, form.surname.data, form.patronymic.data, form.login.data, form.grade.data,
                 form.is_teacher.data))
            if form.grade.data not in [el[1] for el in cursor.execute("SELECT * FROM classes")]:
                cursor.execute('INSERT INTO classes (grade) VALUES (?)', (form.grade.data,))
            connection.commit()
            connection.close()
            return redirect("/main")
        return render_template('add_mcko.html', message="Неправильный секретный код", form=form, name=name)
    return render_template('add_mcko.html', title='Регистрация', form=form, name=name)


@app.route('/class/<int:grade_id>', methods=['GET', 'POST'])
def send_message(grade_id):
    connection = sqlite3.connect("db/2098.db")
    cursor = connection.cursor()
    grade = cursor.execute("SELECT * FROM classes WHERE id = ?", (grade_id,))
    classes = cursor.execute("SELECT * FROM users WHERE grade = ?",
                             (grade.fetchone()[1],)).fetchone()
    connection.close()
    print(classes)
    return render_template('class.html', classes=classes)


# ОПТИМИЗИРУЙ ТВАРЬ!!
@app.route('/ticket/<int:ticket_number>')
def beloved_ticket(ticket_number):
    global name, admin
    if name is None:
        return redirect('/login')
    db_sess = db_session.create_session()
    ticket = db_sess.query(Ticket).filter(Ticket.id == ticket_number).all()[0].to_dict()
    token = "6874396479:AAETyIiiUhpR-pJlW7cwcX0Sd59yDI8jqVc"
    print(ticket_number)
    if os.path.exists('messages/' + str(ticket_number) + 'data.json'):
        with open('messages/' + str(ticket_number) + 'data.json') as json_file:
            data = json.load(json_file)['data']
    else:
        data = []
    for el in get(f'http://api.telegram.org/bot{token}/getUpdates?offset={str(ticket["last_id"])}').json()['result']:
        print(el)
        print(el['message']['chat']['id'], ticket['chat_id'])
        if str(el['message']['chat']['id']) == ticket['chat_id']:
            checker = True
            for elem in data:
                if len(elem) > 3 and elem[3] == el['message']['message_id']:
                    checker = False
            if checker:
                data.append([str(len(data) + 1), el['message']['text'], 1])
    print(data)
    #temp += "{% endblock %}"
    #if data == []:
    #    return render_template('base_ticket.html', title=ticket['problem_name'], ticket=ticket, name=name, messages=data)
    #f = open('templates/ticket.html', 'w', encoding="utf-8")
    #f.write(temp)
    #f.close()
    return render_template('new_ticket.html', title=ticket['problem_name'], ticket=ticket, name=name, messages=data)


@app.route('/add_new_user', methods=['GET', 'POST'])
def register():
    global name, admin
    if name is None:
        redirect('/login')
    if not admin:
        abort(404)
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User(name=form.name.data,
                    email=form.email.data,
                    surname=form.surname.data,
                    last_name=form.last_name.data,
                    login=form.login.data,
                    admin=form.admin.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/my_desk")
    return render_template('register.html', title='Регистрация', form=form, name=name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global name, admin
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.login == form.login.data).first()
        print(user)
        print(form.password.data)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            name = user.surname + ' ' + user.name
            admin = user.admin
            print(name, admin)
            return redirect("/my_desk")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, name=name)
    return render_template('login.html', title='Авторизация', form=form, name=name)


if __name__ == '__main__':
    app.register_blueprint(vocord_tickets_api.blueprint)
    app.run(port=8080, host='127.0.0.1')
    