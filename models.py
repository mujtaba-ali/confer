from enum import unique
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from flask_login import LoginManager

login = LoginManager()
db = SQLAlchemy()

class UserModel(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True)
    email = db.Column(db.String(80), unique = True)
    password_hash = db.Column(db.String())

    def set_pass_hash(self, password):
        self.password_hash = generate_password_hash(password)

    def check_pass_hash(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return UserModel.query.get(int(id))

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    title = db.Column(db.String(80))
    description = db.Column(db.String(500))
    sub = db.Column(db.String(30))
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

'''
    sno
    rollno
    title
    desc
    sub
    timestamp
'''

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qid = db.Column(
    'question',
    db.Integer,
    db.ForeignKey('question.id'),
    nullable=False
    )
    question = db.relationship("Question")
    fname = db.Column(db.String(100))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    qid = db.Column(
    'question',
    db.Integer,
    db.ForeignKey('question.id'),
    nullable=False
    )
    question = db.relationship("Question")
    username = db.Column(db.String(30))
    cmt = db.Column(db.String(100))

