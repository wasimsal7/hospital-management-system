from flask import Flask
from config import LocalDevelopmentConfig
from extensions import db, jwt, cache, celery
from flask_cors import CORS
from routes import bp, admin_bp, user_bp
from models import User
from werkzeug.security import generate_password_hash
from celery import Task
from celery.schedules import crontab

app = Flask(__name__)
app.config.from_object(LocalDevelopmentConfig)
db.init_app(app)
jwt.init_app(app)

app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = app.config['REDIS_URL']
cache.init_app(app)

celery.conf.update(
  broker_url = app.config['CELERY_BROKER_URL'],
  result_backend = app.config['CELERY_RESULT_BACKEND']
)


celery.conf.beat_schedule = {
  'daily_reminders': {
    'task': 'tasks.send_daily_reminders',
    'schedule': crontab(hour=6,minute=0)
  },
  'monthly_reports': {
    'task': 'tasks.send_monthly_reports',
    'schedule': crontab(day_of_month=1, hour=6, minute=0)
  },
}

class ContextTask(Task):
  def __call__(self, *args, **kwargs):
    with app.app_context():
      return self.run(*args, **kwargs)
    
celery.Task = ContextTask

cors = CORS(app, resources={r'*': {'origins': '*'}})

app.register_blueprint(bp)
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)

with app.app_context():
  db.create_all()
  if not User.query.filter_by(role='admin').first():
    admin = User(email='admin@gmail.com', fullname='admin', password=generate_password_hash('admin'), role='admin')
    db.session.add(admin)
    db.session.commit()

if __name__ == '__main__':
  app.run()