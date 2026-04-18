from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from data import db_session
from data.places import Places
from data.users import User
from forms.user import RegisterForm, LoginForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty_zcvbn'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/')
def main():
    db_session.global_init("db/places.db")
    db_sess = db_session.create_session()
    plac = db_sess.query(Places).all()
    return render_template("place.html", places=plac)


@app.route('/place')
def show_place():
    db_session.global_init("db/places.db")
    place_id = request.args.get('id')

    if not place_id:
        return "ID не указан", 400

    tme = datetime.now().strftime("%H")
    db_sess = db_session.create_session()
    place = db_sess.query(Places).get(place_id)
    if int(tme) >= place.open_hour and int(tme) < place.close_hour:
        tr_tme = True
    elif place.open_hour > place.close_hour:
        if (int(tme) + 24 - place.open_hour) >= 0 and (int(tme) + 24 - place.open_hour) < (place.close_hour + 24 - place.open_hour):
            tr_tme = True
        else:
            tr_tme = False
    else:
        tr_tme = False

    if not place:
        return "Место не найдено", 404

    return render_template('places_details.html', place=place, tme=tr_tme)


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    db_session.global_init("db/places.db")
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_session.global_init("db/places.db")
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        else:
            return render_template('login.html',
                                   title='Вход',
                                   form=form,
                                   message='Неправильный email или пароль')
    return render_template('login.html', title='Вход', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')