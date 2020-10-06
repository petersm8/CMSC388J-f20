# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo

# stdlib
import os
from datetime import datetime

# local
from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.model import MovieClient

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/my_database"
app.config['SECRET_KEY'] = b'p\xb0\x95\xddy\xcf\xc4\xcf+%\x87|k+\xe8\xc8'

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
)

mongo = PyMongo(app)

client = MovieClient(os.environ.get('OMDB_API_KEY'))


# --- Do not modify this function ---
@app.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for('query_results', query=form.search_query.data))

    return render_template('index.html', form=form)


@app.route('/search-results/<query>', methods=['GET'])
def query_results(query):
    return render_template('query_results.html', results=client.search(query))


@app.route('/movies/<movie_id>', methods=['GET', 'POST'])
def movie_detail(movie_id):
    mov = client.retrieve_movie_by_id(movie_id)

    form = MovieReviewForm()
    if form.validate_on_submit():
        rev = {
            'commenter': form.name.data,
            'content': form.text.data,
            'date': current_time(),
            'imdb_id': movie_id,
        }
        mongo.db.reviews.insert_one(rev)
        return redirect(request.path)

    review = list(mongo.db.reviews.find({'imdb_id': mov.imdb_id}))
    return render_template('movie_detail.html', movie=mov, reviews=review, form=form)


# Not a view function, used for creating a string for the current time.
def current_time() -> str:
    return datetime.now().strftime('%B %d, %Y at %H:%M:%S')
