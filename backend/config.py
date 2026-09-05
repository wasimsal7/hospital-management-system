class Config():
  DEBUG = False
  SQLALCHEMY_TRACK_MODIFICATIONS = False
  REDIS_URL = 'redis://localhost:6379/0'
  CELERY_BROKER_URL = REDIS_URL
  CELERY_RESULT_BACKEND = REDIS_URL
  GOOGLE_CHAT_WEBHOOK = None # (enter webhook link here)
  MAIL_SERVER = 'localhost'
  MAIL_PORT = 1025
  
class LocalDevelopmentConfig(Config):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = 'sqlite:///database.sqlite3'
  JWT_SECRET_KEY = '987654321'