import pytest

from types import SimpleNamespace
import random
import string

from flask_app.forms import SearchForm, MovieReviewForm
from flask_app.models import User, Review


def rand_str():
    random_string = ''

    for _ in range(10):
        # Considering only upper and lowercase letters
        random_integer = random.randint(97, 97 + 26 - 1)
        flip_bit = random.randint(0, 1)
        # Convert to lowercase if the flip bit is on
        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
        # Keep appending random characters using chr(x)
        random_string += (chr(random_integer))
    return random_string


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200

    search = SimpleNamespace(search_query="guardians", submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)

    assert b"Guardians of the Galaxy" in response.data

    """
    pytest.mark.parametrize
    Test that with an empty query, you get the error "This field is required."
    Test that with a very short string, you get the error "Too many results"
    Test that with some gibberish (maybe a random string?) you get the error "Movie not found"
    Test that with a string that's too long, you get the error "Field must be between 1 and 100 characters long."
    """


@pytest.mark.parametrize(
    ("query", "message"),
    (
            ("", b"This field is required."),
            ("a", b"Too many results"),
            (rand_str(), b"Movie not found!"),
            ("p" * 101, b"Field must be between 1 and 100 characters long."),
    ),
)
def test_search_input_validation(client, query, message):
    search = SimpleNamespace(search_query=query, submit="Search")
    form = SearchForm(formdata=None, obj=search)
    response = client.post("/", data=form.data, follow_redirects=True)
    assert message in response.data


def test_movie_review(client, auth):
    resp = client.get("/login")
    assert resp.status_code == 200
    auth.register()
    response = auth.login()
    with client:
        client.get("/")
    guardians_id = "tt2015381"
    url = f"/movies/{guardians_id}"
    resp = client.get(url)
    assert resp.status_code == 200
    auth.register()
    auth.login()
    r = rand_str()
    rev = SimpleNamespace(
        r=r,
        submit="Enter Comment"
    )
    form = MovieReviewForm(formdata=None, obj=rev)
    with client:
        client.get(url)
        response = client.post(url, data=form.data, follow_redirects=True)

        review = Review.objects(imdb_id=guardians_id).first()
        assert review is not None


@pytest.mark.parametrize(
    ("movie_id", "message"),
    (
            ("", b"404"),
            ("p" * 4, b"Incorrect IMDb ID"),
            ("tt123456789", b"Incorrect IMDb ID"),
            ("p"*11, b"Incorrect IMDb ID"),
    )
)
def test_movie_review_redirects(client, movie_id, message):
    url = f"/movies/{movie_id}"
    response = client.post(url, follow_redirects=False)
    if movie_id == "":
        assert response.status_code == 404
    elif movie_id == "tt123456789":
        assert response.status_code == 302
    else:
        assert response.status_code == 302


@pytest.mark.parametrize(
    ("comment", "message"),
    (
        ("", b"This field is required"),
        ("qwe", b"Field must be between 5 and 500 characters long."),
        ("p"*501, b"Field must be between 5 and 500 characters long.")
    )
)
def test_movie_review_input_validation(client, auth, comment, message):
    guardians_id = "tt2015381"
    auth.register()
    auth.login()
    url = f"/movies/{guardians_id}"
    client.get(url)

    client.post(url, follow_redirects=False)

    r = rand_str()
    rev = SimpleNamespace(
        r=r,
        submit="Enter Comment"
    )
    form = MovieReviewForm(formdata=None, obj=rev)
    with client:
        client.get(url)
        response = client.post(url, data=form.data, follow_redirects=True)
        assert message in response.data
