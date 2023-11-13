# импортируем библиотеку для работы с базой данных
import sqlite3
accesses_lvl = ["Публичная","Общего доступа","Приватная"]
try:
    # создали подключение к бд. если такой базы нет, то она создастся сама
    con = sqlite3.connect(r"db.db", check_same_thread=False)
    # создали курсор для запросов
    cursor = con.cursor()
    # создали таблицу пользователей в базе, если она еще не существует
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS "users" ("id" INTEGER NOT NULL,"login" TEXT NOT NULL, "password" TEXT NOT NULL, primary key("id" AUTOINCREMENT));''')

    # создали таблицу доступа в базе, если ее еще не существует
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS "accesses" ("id" INTEGER NOT NULL,"level" TEXT NOT NULL, primary key("id" AUTOINCREMENT));''')

    # создали таблицу ссылок в базе, если она еще не существует
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS "links" (
        "id" INTEGER NOT NULL, 
        "long" TEXT NOT NULL, 
        "short" TEXT NOT NULL, 
        "count" INTEGER, 
        "owner" INTEGER NOT NULL, 
        "access" INTEGER NOT NULL,
        primary key("id" AUTOINCREMENT),
        FOREIGN KEY ("owner") REFERENCES users("id"),
        FOREIGN KEY ("access") REFERENCES accesses("id")
        );''')
    def find_count_category(cursor):
        cat = cursor.execute('''SELECT COUNT(*) FROM accesses;''').fetchone()
        return cat[0]
    k = 0
    if find_count_category(cursor) < 3:
        while k < 3:
            cursor.execute('''INSERT INTO accesses(level) VALUES (?);''', (accesses_lvl[k],))
            k += 1

    # зафиксировали изменения в базе
    con.commit()

    # функция поиска пользователя в базе
    def find_user(cursor, login, password=False):
        if password:
            return cursor.execute('''SELECT login,password FROM users WHERE login=? AND password=?;''',
                                  (login, password)).fetchone()
        else:
            return cursor.execute('''SELECT * FROM users WHERE login=?;''', (login,)).fetchone()

    def id_user(cursor,login):
        user = cursor.execute('''SELECT id FROM users WHERE login =?''', (login,)).fetchone()
        if user != None:
            return user[0]
        else:
            return None

    def id_lvl(cursor,lvl):
         link = cursor.execute('''SELECT id FROM accesses WHERE level =?''', (lvl,)).fetchone()
         return link[0]

    def add_link(con, cursor, login, long, short, lvl, count = 0):
        user = id_user(cursor,login)
        level = id_lvl(cursor,lvl)
        cursor.execute('''INSERT INTO links(owner, long, short, access, count) VALUES (?,?,?,?,?);''',(user, long, short, level, count))
        con.commit()

    def find_pass(cursor, login):
        return cursor.execute('''SELECT password FROM users WHERE login =?;''', (login,)).fetchone()

    # функция регистрации пользователя
    def registration(connection, cursor, login, password):
        cursor.execute(
            '''INSERT INTO users(login,password) VALUES (?,?) ;''', (login, password))
        connection.commit()

    def change_login(connection, cursor, id, new_log):
        cursor.execute(
            '''UPDATE users SET login=? WHERE id = ?''', (new_log,id)
        )
        connection.commit()

    # функция авторизации пользователя
    def authorize(cursor, login, password):
        return find_user(cursor, login, password)


    # функция удаления пользователя
    def delete_user(connection, cursor, login, password):
        cursor.execute(
            '''DELETE FROM users WHERE login=? AND password=?;''', (login, password))
        connection.commit()


    def view_link(cursor,login):
       user = id_user(cursor,login)
       return cursor.execute('''SELECT id, short, long, access, count FROM links WHERE owner = ?''', (user,)).fetchall()


    def del_links(connection, cursor, id):
        cursor.execute('''DELETE FROM links WHERE id = ?''', (id,))
        connection.commit()

    def countIncrement(link_name, hostname, cursor, con):
        cursor.execute('UPDATE links SET count = count+1 WHERE short = ?', (hostname+link_name,))
        con.commit()

    def find_link (link_name, hostname, cursor, con):

        return cursor.execute('SELECT long, access, owner FROM links WHERE short = ?', (hostname+link_name,)).fetchone()

    def find_link_all (link_name, cursor):
        return cursor.execute('SELECT long, access, owner FROM links WHERE short = ?', (link_name,)).fetchone()

    def findLinkForId (id, cursor):
        return cursor.execute('SELECT * FROM links WHERE id = ?',
                              (id,)).fetchone()

    def changeLinkName(id, cursor ,connect, name):
        cursor.execute('UPDATE links SET short = ? WHERE id = ?', (name, id))
        connect.commit()

    def changeLinkStatus(cursor, con, lvl, id):
        print(id)
        print(lvl)
        cursor.execute('UPDATE links SET access = ? WHERE id = ?', (lvl, id))
        con.commit()




    cursor.close()
except ValueError:
    print("Некорректно введены данные(используйте цифры)")
