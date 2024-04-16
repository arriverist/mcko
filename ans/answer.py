from flask import Flask, render_template, redirect, abort
from requests import get, post
from data import db_session, vocord_tickets_api
from forms.user import RegisterForm, LoginForm, SendForm
from data.users import User
# from forms.ticket import TicketForm
from data.tickets import Ticket
from flask_login import LoginManager, login_required
from flask_login import login_user, logout_user
import os
import json
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


@app.route('/logout')
@login_required
def logout():
    global name, admin
    logout_user()
    name, admin = None, False
    return redirect("/")


@app.route('/my_desk')
def desk():
    global name, admin
    news = []
    in_works = []
    for el in get('http://127.0.0.1:8080/api/all_tickets/0').json()['tickets']:
        news.append([el['id'], el['problem_name'], el['name'], el['product_name'], el['created_at'], "document.location='http://127.0.0.1:8080/ticket/" + str(el['id']) + "'"])
    if name is None:
        return redirect('/login')
    return render_template('desk.html', title='Vocord technical support desk', news=news, in_works=in_works)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.route('/send_message/<int:ticket_number>', methods=['GET', 'POST'])
def send_message(ticket_number):
    form = SendForm()
    if form.validate_on_submit():
        text = form.text.data
        db_sess = db_session.create_session()
        ticket = db_sess.query(Ticket).filter(Ticket.id == ticket_number).all()[0].to_dict()['chat_id']
        token = "6874396479:AAETyIiiUhpR-pJlW7cwcX0Sd59yDI8jqVc"
        post(f'http://api.telegram.org/bot{token}/sendmessage?chat_id={ticket}&text={text}')
        print(os.path.exists('messages/' + str(ticket_number) + 'data.json'), 'messages/' + str(ticket_number) + 'data.json')
        if not os.path.exists('messages/' + str(ticket_number) + 'data.json'):
            with open('messages/' + str(ticket_number) + 'data.json', 'w') as f:
                json.dump({"data": [[str(1), text, 0]]}, f)
            print(1)
        else:
            with open('messages/' + str(ticket_number) + 'data.json', "r") as json_file:
                data = json.load(json_file)["data"]
            data.append([str(len(data) + 1), text, 0])
            print(data)
            with open('messages/' + str(ticket_number) + 'data.json', 'w') as f:
                json.dump({'data': data}, f)
    return render_template('letter.html', title='Письмо', form=form, name=name)


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
    print([ticket["last_id"], ticket["chat_id"], ticket["problem_name"], ticket["name"],])
    print(get(f'http://api.telegram.org/bot{token}/getUpdates?offset={str(ticket["last_id"])}').json(), f'http://api.telegram.org/bot{token}/getUpdates?offset={str(ticket["last_id"])}')
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
    