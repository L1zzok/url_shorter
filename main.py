# библиотеки, база данных
import json
import random, string
from flask import Flask, render_template, url_for, request, redirect, session, make_response, flash, abort
import hashlib
from db import *
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder="templates", static_folder="templates/static")
bcrypt = Bcrypt(app)
Flask.secret_key = os.urandom(10)


menu = {'name': 'Авторизация', 'url': '/auth'},{'name':'Регистрация', 'url': '/reg'}, {'name': 'Главная', 'url': '/index'}, {'name': 'Профиль', 'url': '/profile'}, {'name': 'Мои ссылки', 'url': '/links'}

# переход на главную
@app.route('/')
def index():
    return render_template('index.html', menu=menu)

# переход на форму авторизации
@app.route('/auth')
def auth():
    return render_template('auth.html', menu=menu)

# переход на форму регистрации
@app.route('/reg')
def reg():
    return render_template('reg.html', menu=menu)

# переход в профиль
@app.route('/profile')
def profile():
    if "auth" in session:
        return render_template('profile.html', menu=menu)
    else:
        return redirect(request.host_url+'login')

# выход
@app.route('/logout')
def logout():
    session.pop('auth', None)
    session.pop('name', None)
    return redirect(request.host_url)

# удаление ссылки
@app.route('/del', methods = ["GET"])
def del_link():
    con = sqlite3.connect(r"db.db", check_same_thread=False)
    cursor = con.cursor()
    id = request.args.get('id')
    del_links(con, cursor,id)
    return redirect(request.host_url+'links')

# регистрация
@app.route('/reg', methods= ['POST', "GET"])
def registr():
    if request.method == 'POST':
        con = sqlite3.connect(r"db.db", check_same_thread=False)
        cursor = con.cursor()
        login = request.form["username"]
        password = request.form["password"]
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        if find_user(cursor, login) == None:
            registration(con, cursor, login, hashed_password)
            session['name'] = login
            session['auth'] = True
            return redirect(request.host_url+'profile')
        else:
            flash(f"Этот логин ({login}) уже есть в базе")
            return redirect(f'/reg')

# авторизация
@app.route('/auth', methods= ['POST', "GET"])
def authh():
    if request.method == 'POST':
        con = sqlite3.connect(r"db.db", check_same_thread=False)
        cursor = con.cursor()
        login = request.form["username"]
        password = request.form["password"]
        if find_user(cursor, login) != None:
            hashed_password = find_pass(cursor, login)
            hashedd = hashed_password[0]
            is_valid = bcrypt.check_password_hash(hashedd, password)
            if is_valid == True:
                authorize(cursor, login, hashedd)
                session['name'] = login
                id = id_user(cursor, login)
                session['id'] = id
                session['auth'] = True
                return redirect(f'{request.host_url}/profile')
            else:
                flash(f"Пароль введен неверно")
                return redirect(f'/auth')
        else:
            flash(f"Пользователь не найден")
            return redirect(f'/auth')

# добавление ссылки
@app.route('/links', methods= ['POST'])
def addLink():
    if request.method == 'POST':
        con = sqlite3.connect(r"db.db")
        cursor = con.cursor()
        login = session['name']
        lvl = request.form['lvl']
        long = request.form['long']
        if request.form['short'] is not None and request.form['short'] != "":
            short = request.host_url + request.form['short']

        else:
            short = request.host_url+ hashlib.md5(long.encode()).hexdigest()[:random.randint(8, 12)]
        if session['auth'] == True:
            if find_link_long(long, session["id"], cursor) == None:
                print(find_link_long(long, session["name"], cursor))
                if find_link_all(short, cursor) == None:
                    add_link(con, cursor, login, long, short, lvl)
                    return redirect(request.host_url+'links', code=302)
                else:
                    flash("Введите другой псевдоним", category="error")
                    return redirect(request.host_url +'links' , code=302)
            else:
                flash("Данная ссылка у вас уже есть", category="error")
                return redirect(request.host_url + 'links', code=302)

        else:
            return f"Вы не авторизованы"

# вывод всех ссылок пользователя
@app.route('/links')
def view_linkss():
    con = sqlite3.connect(r"db.db")
    cursor = con.cursor()
    login = session['name']
    if session['auth'] == True:
        arr = view_link(cursor, login)
        return render_template('links.html', arr = arr)

# изменение никнейма юзера
@app.route('/profile', methods= ["POST"])
def change_user():
    if request.method == "POST":
        con = sqlite3.connect(r"db.db")
        cursor = con.cursor()
        new_login = request.form['login']
        if find_user(cursor, new_login) == None:
            session['name'] = new_login
            id = request.form['id']
            change_login(con,cursor, id,new_login)
        else:
            flash(f"Этот логин ({new_login}) уже есть в базе")
            return redirect(f'/profile')

    return redirect(request.host_url+'profile')


@app.route('/<link>')
def linkGo(link):
    con = sqlite3.connect(r"db.db")
    cursor = con.cursor()
    full_link = find_link (link, request.host_url, cursor)
    if full_link != None:
        if (full_link[1] == 1):
            countIncrement(link, request.host_url, cursor, con)
            return  redirect( full_link[0])

        if (full_link[1] == 2):
            if(session.get('auth')):
                countIncrement(link, request.host_url, cursor, con)
                return redirect(full_link[0])
            else:
                return redirect(f'/auth/page/{link}')

        if (full_link[1] ==3):

            user_id = id_user(cursor, session.get('name'))
            if(user_id != full_link[2]):
                flash('Ссылка не ваша, а доступ приватный')
                return redirect(f'/auth/page/{link}')
            else:
                countIncrement(link, request.host_url, cursor, con)
                return redirect(full_link[0])
    else:
        abort(404)


@app.route('/auth/page/<link>', methods= ['POST', "GET"])
def authForLinkPage(link):
    return render_template('authSSL.html', menu=menu, link= link)
@app.route('/auth/<link>', methods= ['POST', "GET"])
def authForLink(link):
    if request.method == 'POST':
        con = sqlite3.connect(r"db.db", check_same_thread=False)
        cursor = con.cursor()
        login = request.form["username"]
        password = request.form["password"]
        if find_user(cursor, login) != None:
            hashed_password = find_pass(cursor, login)
            hashedd = hashed_password[0]
            is_valid = bcrypt.check_password_hash(hashedd, password)
            if is_valid == True:
                authorize(cursor, login, hashedd)
                session['name'] = login
                id = id_user(cursor,login)
                session['id'] = id
                session['auth'] = True
                full_link = find_link(link, request.host_url, cursor)
                return redirect(f'/{link}')

            else:
                flash(f"Пароль введен неверно")
                return redirect(f'/auth/page/{link}')
        else:
            flash(f"Пользователь не найден")
            return redirect(f'/auth/page/{link}')
@app.route('/gethostname', methods= ['POST', "GET"])
def gethostname():
    # full_link = find_link(link, request.host_url, cursor)
    return json.dumps(request.host_url)

@app.route('/getLinkName', methods= ['POST', "GET"])
def getLinkName():
    if request.method == "POST":
        con = sqlite3.connect(r"db.db", check_same_thread=False)
        cursor = con.cursor()
        data = json.loads(request.data)
        print(data)
        id = int(data['id'])

        link = findLinkForId (id, cursor)
        return json.dumps(link[2])
    else:
        return redirect("/", code=302)

@app.route("/changeLinkNickName", methods = ["POST"])
def changeLinkNickName():
    if request.method == "POST":
        con = sqlite3.connect(r"db.db", check_same_thread=False)
        cursor = con.cursor()
        link_name = request.form["nickName"]
        id = request.form.get("id")
        random1 = request.form.get('random')
        if id != None:
            if (find_link (link_name, request.host_url, cursor) != None):
                flash("Введите другой псевдоним", category="error")
                return redirect("/links", code=302)
            print(changeLinkName(id, cursor,con, request.host_url+link_name))
            return redirect("/links", code=302)
        if random1 != None:
            letters = string.ascii_lowercase

            link_name_for_random = request.host_url+ ''.join(random.choice(letters) for i in range(random.randint(8, 12)))
            if (find_link(link_name_for_random, request.host_url, cursor) != None):
                link_name_for_random = request.host_url + ''.join(
                    random.choice(letters) for i in range(random.randint(8, 12)))
            changeLinkName(random1, cursor, con, link_name_for_random)
            return redirect("/links", code=302)


@app.route("/changeLinkStatus", methods = ["POST"])
def changeLinkStatusPage():
    if request.method == "POST":
        con = sqlite3.connect(r"db.db", check_same_thread=False)
        cursor = con.cursor()
        lvl = request.form.get("lvl")
        id = request.form.get("id")
        changeLinkStatus(cursor, con, lvl, id)
        return redirect("/links", code=302)


if __name__ == "__main__":
    app.run(debug=True)
