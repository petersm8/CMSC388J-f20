import base64
import io

from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()


class User(db.Document, UserMixin):
    username = db.StringField(unique=True, required=True)
    email = db.EmailField(unique=True, required=True)
    password = db.StringField()
    profile_pic = db.ImageField()

    # Returns unique string identifying our object
    def get_id(self):
        return self.username

    def get_b64_img(self):
        bytes_im = io.BytesIO(self.profile_pic.read())
        image = base64.b64encode(bytes_im.getvalue()).decode()
        return image


class Review(db.Document):
    commenter = db.ReferenceField(User)
    content = db.StringField(required=True)
    date = db.StringField()
    imdb_id = db.StringField()
    movie_title = db.StringField()
