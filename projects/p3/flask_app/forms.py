from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class SearchForm(FlaskForm):
    search_query = StringField('Query', validators=[DataRequired(), Length(min=1, max=30)])
    submit = SubmitField('Submit Search!')


class MovieReviewForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=50)])
    text = TextAreaField('Review', validators=[DataRequired(), Length(min=1, max=500)])
    submit = SubmitField('Submit Review!')
