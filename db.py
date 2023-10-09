# импортируем библиотеку для работы с базой данных
import sqlite3

try:
    # создали подключение к бд. если такой базы нет, то она создастся сама
    con = sqlite3.connect(r"db.db", check_same_thread=False)
    # создали курсор для запросов
    cursor = con.cursor()
    # создали таблицу в базе, если она еще не существует
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS "users" ("id" INTEGER NOT NULL,"login" TEXT NOT NULL, "password" TEXT NOT NULL, primary key("id" AUTOINCREMENT));''')
    # зафиксировали изменения в базе
    con.commit()


    # функция поиска пользователя в базе
    def find_user(cursor, login, password=False):
        if password:
            return cursor.execute('''SELECT login,password FROM users WHERE login=? AND password=?;''',
                                  (login, password)).fetchone()
        else:
            return cursor.execute('''SELECT * FROM users WHERE login=?;''', (login,)).fetchone()


    # функция регистрации пользователя
    def registration(connection, cursor, login, password):
        cursor.execute(
            '''INSERT INTO users(login,password) VALUES (?,?) ;''', (login, password))
        connection.commit()


    # функция авторизации пользователя
    def authorize(cursor, login, password):
        return find_user(cursor, login, password)


    # функция удаления пользователя
    def delete_user(connection, cursor, login, password):
        cursor.execute(
            '''DELETE FROM users WHERE login=? AND password=?;''', (login, password))
        connection.commit()

    cursor.close()

#     while True:
#         # запросили действие
#         act = int(input(
#             "Что вы хотите сделать? регистрация - 1, авторизация - 2, выйти - 3, удалить пользователя - 4\n"))
#         # выход из цикла
#         if act == 3:
#             break
#         else:
#             # запросили логин и пароль
#             login = input("введите логин ")
#             password = input("введите пароль ")
#
#             # регистрация
#             if act == 1:
#                 if find_user(cursor, login, password):
#                     print("Пользователь с такими данными уже зарегистрирован")
#                 else:
#                     registration(con, cursor, login, password)
#                     print("Пользователь успешно зарегистрирован")
#
#             # авторизация
#             if act == 2:
#                 if authorize(cursor, login, password):
#                     print("Авторизация успешна")
#                 else:
#                     print("Неверный логин или пароль")
#
#             # удаление пользователя
#             if act == 4:
#                 if find_user(cursor, login, password):
#                     delete_user(con, cursor, login, password)
#                     print("Пользователь успешно удалён")
#                 else:
#                     print("Пользователь с такими данными не найден")
#     # закрыли подключение

#
except ValueError:
    print("Некорректно введены данные(используйте цифры)")
