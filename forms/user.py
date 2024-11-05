from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, EmailField, BooleanField, StringField, DateField, TextAreaField
from wtforms.validators import DataRequired

numbers = ("Первое Второе Третье Четвертое Пятое Шестое Седьмое Восьмое Девятое Десятое Одиннадцатое Двенадцатое " +
           "Тринадцатое Четырнадцатое Пятнадцатое Шестнадцатое Семнадцатое Восемнадцатое " +
           "Девятнадцатое Двадцатое Двадцать-первое" +
           " Двадцать-второе Двадцать-третье Двадцать-четвертое Двадцать-пятое").split()

class RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    last_name = StringField('Отчество')
    email = EmailField('Почта', validators=[DataRequired()])
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    admin = BooleanField('Сделать администратором?')
    submit = SubmitField('Добавить')


class SendForm(FlaskForm):
    text = TextAreaField('Текст сообщения', validators=[DataRequired()])
    submit = SubmitField('Отправить')


class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class mcko_LoginForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    login = StringField("Логин", validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class mcko_RegisterForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    patronymic = StringField('Отчество', validators=[DataRequired()])
    login = StringField("Логин", validators=[DataRequired()])
    is_teacher = BooleanField('Учитель')
    grade = StringField('Класс', validators=[DataRequired()])
    secret_code = StringField('Секретный код', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class mcko_TestForm(FlaskForm):
    global numbers
    name = StringField('Название демоверсии: ', validators=[DataRequired()])
    name.name = "name"
    print(numbers)
    tasks = [StringField(numbers[i] + " задание") for i in range(25)]
    for i in range(25):
        tasks[i].name = "task_" + str(i + 1)
    submit = SubmitField('Добавить')