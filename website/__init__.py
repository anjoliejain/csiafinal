from flask import Flask, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from os import path
from flask_login import LoginManager
from fpdf import FPDF

db = SQLAlchemy()
DB_NAME = "arpwood.db"

def create_app():
    app = Flask(__name__)
    app.secret_key = 'very secret key'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note, Deals, TeamNotes

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')