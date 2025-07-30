from flask import Flask
from app.db import init_db
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # 初始化数据库
    init_db(app)
    # 注册蓝图
    from app.views import admin
    from app.views import employer
    from app.views import student
    from app.views import user

    app.register_blueprint(admin.bp)
    app.register_blueprint(employer.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(user.bp)

    return app
