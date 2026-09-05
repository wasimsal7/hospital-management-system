from extensions import celery, db
from models import Appointment, User, Download, History
from datetime import datetime, timedelta
from flask import current_app, render_template
import requests
import smtplib
from email.message import EmailMessage
import csv
import os

@celery.task
def send_daily_reminders():
  today = datetime.now().date()
  appointments = Appointment.query.filter_by(date=today, status='booked').all()
  webhook = current_app.config['GOOGLE_CHAT_WEBHOOK']
  for appointment in appointments:
    patient = appointment.patient.fullname
    doctor = appointment.doctor.fullname
    time = appointment.time
    message = {'text': f'Reminder: {patient} has an appointment with Dr. {doctor} at {time} today.'}
    requests.post(webhook, json=message)
  return f'Sent {len(appointments)} reminders.'

@celery.task
def send_monthly_reports():
  today = datetime.now() + timedelta(days=30)
  last_day = today.replace(day=1) - timedelta(days=1)
  first_day = last_day.replace(day=1)
  doctors = User.query.filter_by(role='doctor').all()
  for doctor in doctors:
    appointments = History.query.filter(History.doctor_id==doctor.id, History.status=='completed', History.date>=first_day, History.date<=last_day).all()
    html_report = render_template('monthly_report.html', doctor=doctor, appointments=appointments)
    msg = EmailMessage()
    msg['Subject'] = 'Monthly Report'
    msg['From'] = 'admin@gmail.com'
    msg['To'] = doctor.email
    msg.set_content(html_report, subtype='html')
    with smtplib.SMTP(
      current_app.config['MAIL_SERVER'],
      current_app.config['MAIL_PORT'],
    ) as server:
      server.send_message(msg)
  return f'Sent {len(doctors)} reports.'

@celery.task
def export_patient_csv(patient_id, doctor_id):
  filename=f'patient_{patient_id}_{datetime.now().timestamp()}.csv'
  download = Download(patient_id=patient_id, filename=filename)
  db.session.add(download)
  db.session.commit()
  export_dir = os.path.join(current_app.root_path, 'exports')
  os.makedirs(export_dir, exist_ok=True)
  filepath = os.path.join(export_dir, filename)
  appointments = History.query.filter_by(patient_id=patient_id, doctor_id=doctor_id, status='completed').all()
  with open(filepath, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([
      'Date', 'Time', 'Patient', 'Doctor', 'Diagnosis', 'Prescription', 'Notes',
    ])
    for appointment in appointments:
      writer.writerow([
        appointment.date, appointment.time, appointment.patient, appointment.doctor, appointment.diagnosis, appointment.prescription, appointment.notes
      ])
  download.status='completed'
  db.session.commit()
  return download.filename

@celery.task
def reject_request(doctor_id, reason, change):
  doctor = User.query.get(doctor_id)
  msg = EmailMessage()
  msg['Subject'] = 'Request Rejected.'
  msg['From'] = 'admin@gmail.com'
  msg['To'] = doctor.email
  msg.set_content(f"""Your request for {change} change has been rejected.
                  Reason: {reason}""")
  with smtplib.SMTP(
    current_app.config['MAIL_SERVER'],
    current_app.config['MAIL_PORT']
  ) as server:
    server.send_message(msg)
  return 'Email sent.'