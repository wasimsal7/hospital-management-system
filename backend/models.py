from extensions import db
from datetime import datetime

class User(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String, unique=True, nullable=False)
  fullname = db.Column(db.String, nullable=False)
  password = db.Column(db.String, nullable=False)
  role = db.Column(db.String, nullable=False, default='patient')
  department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
  doctor_availability = db.relationship('Availability', cascade='all, delete') 
  doctor = db.relationship('DoctorProfile', backref='user_ref', uselist=False, cascade='all, delete') 

class DoctorProfile(db.Model):
  __tablename__ = 'doctor_profile'
  id = db.Column(db.Integer, primary_key=True)
  doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
  fullname = db.Column(db.String, nullable=False)
  department = db.Column(db.String, nullable=False)
  experience = db.Column(db.String, nullable=False)
  about = db.Column(db.String, nullable=False)
  change = db.relationship('RequestChange', backref='doc_profile_ref')

class RequestChange(db.Model):
  __tablename__ = 'request_change'
  id = db.Column(db.Integer, primary_key=True)
  doctor_profile_id = db.Column(db.Integer, db.ForeignKey('doctor_profile.id'), nullable=False)
  change = db.Column(db.String, nullable=False)
  value = db.Column(db.String, nullable=False)
  notes = db.Column(db.String, nullable=False)

class Availability(db.Model):
  __tablename__ = 'availability'
  id = db.Column(db.Integer, primary_key=True)
  doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  date = db.Column(db.Date, nullable=False)
  slot = db.Column(db.String, nullable=False)
  is_available = db.Column(db.Boolean, nullable=False, default=False)
  limit = db.Column(db.Integer, nullable=False, default=3)

class Appointment(db.Model):
  __tablename__ = 'appointment'
  id = db.Column(db.Integer, primary_key=True)
  patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  date = db.Column(db.Date, nullable=False)
  time = db.Column(db.String, nullable=False)
  status = db.Column(db.String, nullable=False, default='booked')
  cancelled_by = db.Column(db.String, nullable=True)
  patient = db.relationship('User', foreign_keys=[patient_id])
  doctor = db.relationship('User', foreign_keys=[doctor_id])
  treatment = db.relationship('Treatment', backref='appointment_ref', uselist=False, cascade='all, delete')

class Treatment(db.Model):
  __tablename__ = 'treatment'
  id = db.Column(db.Integer, primary_key = True)
  appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), unique=True, nullable=False)
  diagnosis = db.Column(db.String, nullable=False)
  prescription = db.Column(db.String, nullable=False)
  notes = db.Column(db.String, nullable=False)

class History(db.Model):
  __tablename__ = 'history'
  id = db.Column(db.Integer, primary_key=True)
  appointment_id = db.Column(db.Integer, unique=True, nullable=False)
  patient_id = db.Column(db.Integer, nullable=False)
  patient = db.Column(db.String, nullable=False)
  doctor_id = db.Column(db.Integer, nullable=False)
  doctor = db.Column(db.String, nullable=False)
  department = db.Column(db.String, nullable=False)
  date = db.Column(db.Date, nullable=False)
  time = db.Column(db.String, nullable=False)
  status = db.Column(db.String, nullable=False)
  cancelled_by = db.Column(db.String, nullable=True)
  diagnosis = db.Column(db.String, nullable=True)
  prescription = db.Column(db.String, nullable=True)
  notes = db.Column(db.String, nullable=True)

class Department(db.Model):
  __tablename__ = 'department'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, unique=True, nullable=False)
  description = db.Column(db.String, nullable=False)
  doctor_registered = db.relationship('User', backref='department_ref')

class Download(db.Model):
  __tablename__ = 'download'
  id = db.Column(db.Integer, primary_key=True)
  patient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  filename = db.Column(db.String, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
  status = db.Column(db.String, nullable=False, default='processing')