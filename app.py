from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from data import db_session
from data.places import Places
from data.users import User
from forms.user import RegisterForm, LoginForm
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty_zcvbn'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@app.route('/')
def main():
    db_sess = db_session.create_session()
    query = db_sess.query(Places)

    filter_by = request.args.get('filter')
    filter_value = request.args.get('value')
    if filter_by == 'category' and filter_value:
        query = query.filter(Places.category == filter_value)

    sort_by = request.args.get('sort')
    if sort_by == 'title_asc':
        query = query.order_by(Places.title.asc())
    elif sort_by == 'title_desc':
        query = query.order_by(Places.title.desc())
    elif sort_by == 'open_asc':
        query = query.order_by(Places.open_hour.asc())
    elif sort_by == 'open_desc':
        query = query.order_by(Places.open_hour.desc())
    elif sort_by == 'close_asc':
        query = query.order_by(Places.close_hour.asc())
    elif sort_by == 'close_desc':
        query = query.order_by(Places.close_hour.desc())
    else:
        query = query.order_by(Places.id)

    places = query.all()
    return render_template('place.html', places=places)


@app.route('/place')
def show_place():
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

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user, title='Мой профиль')


@app.route('/like_place/<int:place_id>', methods=['POST'])
@login_required
def like_place(place_id):
    liked = json.loads(current_user.liked_places) if current_user.liked_places else []
    if place_id in liked:
        liked.remove(place_id)
    else:
        liked.append(place_id)
    current_user.liked_places = json.dumps(liked)
    db.session.commit()
    return redirect(request.referrer or url_for('main'))

@app.route('/registration', methods=['GET', 'POST'])
def registration():
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
        login_user(user, remember=False)
        return redirect('/')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
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
    db_session.global_init("db/places.db")
    app.run(port=8080, host='0.0.0.0')