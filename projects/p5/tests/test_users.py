from flask import session, request
import pytest

from types import SimpleNamespace

from flask_app.forms import RegistrationForm, UpdateUsernameForm
from flask_app.models import User


def test_register(client, auth):
    """ Test that registration page opens up """
    resp = client.get("/register")
    assert resp.status_code == 200

    response = auth.register()

    assert response.status_code == 200
    user = User.objects(username="test").first()

    assert user is not None


@pytest.mark.parametrize(
    ("username", "email", "password", "confirm", "message"),
    (
            ("test", "test@email.com", "test", "test", b"Username is taken"),
            ("p" * 41, "test@email.com", "test", "test", b"Field must be between 1 and 40"),
            ("username", "test", "test", "test", b"Invalid email address."),
            ("username", "test@email.com", "test", "test2", b"Field must be equal to"),
    ),
)
def test_register_validate_input(auth, username, email, password, confirm, message):
    if message == b"Username is taken":
        auth.register()

    response = auth.register(username, email, password, confirm)

    assert message in response.data


def test_login(client, auth):
    """ Test that login page opens up """
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
            ("", "", b"This field is required"),
            ("testy1", "test", b"Login failed. Check your username and/or password"),
    ),
)
def test_login_input_validation(auth, username, password, message):
    auth.register()
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    auth.login()

    with client:
        client.get("/")
        assert session["_user_id"] == "test"
        auth.logout()
        resp = client.get("/login")
        assert resp.status_code == 200


def test_change_username(client, auth):
    resp = client.get("/login")
    assert resp.status_code == 200
    auth.register()
    response = auth.login()
    with client:
        client.get("/")
        assert session["_user_id"] == "test"
        client.get("/account")
        user = SimpleNamespace(username="testy", submit="Update Username")
        form = UpdateUsernameForm(formdata=None, obj=user)
        response = client.post("/account", data=form.data, follow_redirects=True)
        client.get("/")
        assert session["_user_id"] == "testy"


def test_change_username_taken(client, auth):
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()

    resp = client.get("/account")
    user = SimpleNamespace(username="test", submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=user)
    response = client.post("/", data=form.data, follow_redirects=True)
    assert b"That username is already taken" in response.data
    client.get("/")
    assert session["_user_id"] == "test"


@pytest.mark.parametrize(
    ("new_username",),
    (("",),
     ("p" * 41,),
     )
)
def test_change_username_input_validation(client, auth, new_username):
    resp = client.get("/login")
    assert resp.status_code == 200

    auth.register()
    response = auth.login()
    user = SimpleNamespace(username="test", submit="Update Username")
    form = UpdateUsernameForm(formdata=None, obj=user)
    response = client.post("/", data=form.data, follow_redirects=True)
    if new_username == "":
        assert b"This field is required." in response.data
    elif new_username == "p"*41:
        assert b"Field must be between 1 and 40 characters long." in response.data
