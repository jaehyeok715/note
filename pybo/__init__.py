from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

import config

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    # ORM
    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    # 블루프린트
    from .views import main_views, auth_views, group_calendar  #블루프린트로 만든 파이썬파일 이름 적기
    app.register_blueprint(main_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(group_calendar.bp)


    return app
