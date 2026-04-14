from flask import Flask, render_template, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from data import db_session
from data.places import Places
from data.users import User
from forms.user import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '?'


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
        return redirect('/main')
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/main')
def main():
    db_session.global_init("db/places.db")
    db_sess = db_session.create_session()
    place = db_sess.query(Places)
    print(place)
    return render_template("place.html", places=place)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')