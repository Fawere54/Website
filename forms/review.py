from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length


class ReviewForm(FlaskForm):
    text = TextAreaField('Ваш отзыв', validators=[DataRequired(), Length(min=5, max=1000)])
    rating = IntegerField('Оценка (1–5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField('Отправить отзыв')
