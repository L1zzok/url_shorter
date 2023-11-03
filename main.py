import random

from flask import Flask, render_template, url_for, request, redirect, session, make_response, flash
import hashlib
from db import *
import os
from flask_bcrypt import Bcrypt

app = Flask(__name__, template_folder="templates", static_folder="templates/static")
bcrypt = Bcrypt(app)
Flask.secret_key = os.urandom(10)


menu = {'name': 'Авторизация', 'url': '/auth'},{'name':'Регистрация', 'url': '/reg'}, {'name': 'Главная', 'url': '/index'}, {'name': 'Профиль', 'url': '/profile'}, {'name': 'Мои ссылки', 'url': '/links'}

@app.route('/')
def index():
    return render_template('index.html', menu=menu)

@app.route('/auth')
def auth():
    return render_template('auth.html', menu=menu)

# @app.route('/links')
# def links():
#     return render_template('links.html', menu=menu)

@app.route('/reg')
def reg():
    return render_template('reg.html', menu=menu)

@app.route('/profile')
def profile():
    if "auth" in session:
        return render_template('profile.html', menu=menu)
    else:
        return redirect('http://127.0.0.1:5000/login')

@app.route('/logout')
def logout():
    session.pop('auth', None)
    return redirect('http://127.0.0.1:5000/')

@app.route('/del', methods = ["GET"])
def del_link():
    con = sqlite3.connect(r"db.db", check_same_thread=False)
    cursor = con.cursor()
    id = request.args.get('id')
    del_links(con, cursor,id)
    return redirect('http://127.0.0.1:5000/links')


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
            return redirect('http://127.0.0.1:5000/profile')
        else:
            message = f"Этот логин ({login}) уже есть в базе"
            return message

@app.route('/auth', methods= ['POST', "GET"])
def authh():
    if request.method == 'POST':
        con = sqlite3.connect(r"db.db", check_same_thread=False)
        cursor = con.cursor()
        login = request.form["username"]
        password = request.form["password"]
        hashed_password = find_pass(cursor, login)
        hashedd = hashed_password[0]
        is_valid = bcrypt.check_password_hash(hashedd, password)
        if find_user(cursor, login) != None:
            if is_valid == True:
                authorize(cursor, login, hashedd)
                session['name'] = login
                id = id_user(cursor,login)
                session['id'] = id
                session['auth'] = True
                return redirect('http://127.0.0.1:5000/profile')
            else:
                return f"Пароль введен неверно"
        else:
            return f"Пользователь не найден"

@app.route('/links', methods= ['POST'])
def addLink():
    if request.method == 'POST':
        con = sqlite3.connect(r"db.db")
        cursor = con.cursor()
        login = session['name']
        lvl = request.form['lvl']
        long = request.form['long']
        if request.form['short'] is not None and request.form['short'] != "":
            short = "https://" + request.form['short']

        else:
            short = "https://" + hashlib.md5(long.encode()).hexdigest()[:random.randint(8, 12)]
        if session['auth'] == True:

            add_link(con, cursor, login, long, short, lvl)
            return redirect('http://127.0.0.1:5000/links')
        else:
            return f"Вы не авторизованы"

@app.route('/links')
def view_linkss():
    con = sqlite3.connect(r"db.db")
    cursor = con.cursor()
    login = session['name']
    if session['auth'] == True:
        arr = view_link(cursor, login)
        return render_template('links.html', arr = arr)

@app.route('/profile', methods= ["POST"])
def change_user():
    if request.method == "POST":
        con = sqlite3.connect(r"db.db")
        cursor = con.cursor()
        new_login = request.form['login']
        session['name'] = new_login
        id = request.form['id']
        print(new_login)
        print(id)
        change_login(con,cursor, id,new_login)

    return redirect('http://127.0.0.1:5000/profile')


if __name__ == "__main__":
    app.run(debug=True)