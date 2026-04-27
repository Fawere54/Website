from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from data import db_session
from data.places import Places
from data.users import User
from data.reviews import Review
from data.reviews_db_session import create_reviews_session, global_init_reviews
from forms.user import RegisterForm, LoginForm
from forms.review import ReviewForm
from sqlalchemy import func
from datetime import datetime

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

    rev_sess = create_reviews_session()
    stats = rev_sess.query(
        Review.place_id,
        func.avg(Review.rating).label('avg_rating'),
        func.count(Review.id).label('reviews_count')
    ).group_by(Review.place_id).all()
    rev_sess.close()
    ratings = {stat.place_id: (round(stat.avg_rating, 1) if stat.avg_rating else 0, stat.reviews_count) for stat in
               stats}

    db_sess.close()
    return render_template('place.html', places=places, ratings=ratings)


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
        if (int(tme) + 24 - place.open_hour) >= 0 and (int(tme) + 24 - place.open_hour) < (
                place.close_hour + 24 - place.open_hour):
            tr_tme = True
        else:
            tr_tme = False
    else:
        tr_tme = False

    if not place:
        return "Место не найдено", 404

    rev_sess = create_reviews_session()
    reviews = rev_sess.query(Review).filter(Review.place_id == place_id).order_by(Review.created_date.desc()).all()
    rev_sess.close()
    form = ReviewForm()
    db_sess.close()
    return render_template('places_details.html', place=place, tme=tr_tme, reviews=reviews, form=form)


@app.route('/add_review/<int:place_id>', methods=['POST'])
@login_required
def add_review(place_id):
    form = ReviewForm()
    if form.validate_on_submit():
        rev_sess = create_reviews_session()
        review = Review(
            text=form.text.data,
            rating=form.rating.data,
            user_id=current_user.id,
            user_name=current_user.name,
            place_id=place_id
        )
        rev_sess.add(review)
        rev_sess.commit()
        rev_sess.close()
    return redirect(url_for('show_place', id=place_id))


@app.route('/profile')
@login_required
def profile():
    db_sess = db_session.create_session()
    user = db_sess.get(User, current_user.id)
    fav_ids = user.favorites.split(',') if user.favorites else []
    favorite_places = []
    if fav_ids:
        favorite_places = db_sess.query(Places).filter(Places.id.in_(fav_ids)).all()
    db_sess.close()
    return render_template('profile.html', favorite_places=favorite_places)


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
            email=form.email.data,
            favorites=''
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
    with db_session.create_session() as db_sess:
        return db_sess.query(User).get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/add_to_favorites/<int:place_id>')
@login_required
def add_to_favorites(place_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(current_user.id)
    fav_list = user.favorites.split(',') if user.favorites else []
    pid = str(place_id)

    if pid in fav_list:
        fav_list.remove(pid)
        status = "removed"
    else:
        fav_list.append(pid)
        status = "added"

    user.favorites = ",".join(filter(None, fav_list))
    db_sess.commit()
    db_sess.close()
    return jsonify({"status": status, "place_id": place_id})


if __name__ == '__main__':
    db_session.global_init("db/places.db")
    global_init_reviews("db/reviews.db")
    app.run(port=8080, host='0.0.0.0')
