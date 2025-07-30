import pymysql


def init_db(app):
    """初始化数据库配置"""
    # pymysql 没有内置连接池，这里只是存储配置
    app.db_config = {
        'host': app.config['MYSQL_HOST'],
        'user': app.config['MYSQL_USER'],
        'password': app.config['MYSQL_PASSWORD'],
        'database': app.config['MYSQL_DB'],
        'charset': 'utf8mb4'
    }


def get_db_conn():
    """创建数据库连接"""
    from flask import current_app
    return pymysql.connect(**current_app.db_config)
