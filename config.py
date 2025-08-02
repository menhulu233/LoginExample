import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'localhost123'
    MYSQL_DB = 'BrightPathCareers'
    MYSQL_PORT = 3306
    BOOTSTRAP_SERVE_LOCAL = True  # 本地加载Bootstrap资源
