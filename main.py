from flask import Flask, render_template, url_for
app = Flask(__name__, template_folder="templates", static_folder="templates/static")

menu = {'name': 'Авторизация', 'url': '/auth'},{'name':'Регистрация', 'url': '/reg'}, {'name': 'Главная', 'url': '/index'}

@app.route('/index')
def index():
    return render_template('index.html', menu=menu)

@app.route('/auth')
def auth():
    return render_template('auth.html', menu=menu)

@app.route('/reg')
def reg():
    return render_template('reg.html', menu=menu)

if __name__ == "__main__":
    app.run(debug=True)