from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime
import pytz
import time


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now(pytz.timezone('Asia/Calcutta')))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')


class Deals(db.Model):
    dealid = db.Column(db.String(100), primary_key=True)
    clientid = db.Column(db.String(100))
    dealname = db.Column(db.String(100))
    comments = db.Column(db.String(1000))
    dealstatus = db.Column(db.String(100))
    date = db.Column(db.String(100))
    datecreated = db.Column(db.String(100))


class TeamNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    update = db.Column(db.String(100))
    deal_id = db.Column(db.String(100), db.ForeignKey('deals.dealid'))




