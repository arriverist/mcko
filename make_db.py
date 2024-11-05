import sqlite3

# Устанавливаем соединение с базой данных
connection = sqlite3.connect('2098.db')
cursor = connection.cursor()

# Создаем таблицу Users
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
id INTEGER PRIMARY KEY UNIQUE,
name TEXT NOT NULL,
surname TEXT NOT NULL,
patronymic TEXT NOT NULL,
login TEXT NOT NULL,
grade TEXT NOT NULL,
is_teacher TEXT NOT NULL
)
''')
cursor.execute('''
CREATE TABLE classes (
id INTEGER PRIMARY KEY UNIQUE,
grade TEXT NOT NULL
)
''')
cursor.execute('INSERT INTO users (name, surname, patronymic, login, grade, is_teacher) VALUES (?, ?, ?, ?, ?, ?)',
               ('Тимофей', 'Перунов', 'Николаевич', 'login', '10Т', '1'))
cursor.execute('INSERT INTO classes (grade) VALUES (?)',
               ('10Т',))
# Сохраняем изменения и закрываем соединение
connection.commit()
connection.close()