from functools import wraps
from flask import Blueprint, request, jsonify, current_app, send_file
from models import User, Appointment, Treatment, Department, Availability, DoctorProfile, Download, RequestChange, History
from extensions import db, cache
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from tasks import export_patient_csv, reject_request
import os

bp = Blueprint('main', __name__)

# Auth Routes

@bp.route('/login', methods=['POST'])
def login():
  data = request.get_json()
  email = data.get('email')
  password = data.get('password')
  user = User.query.filter_by(email=email).first()
  if not user or not check_password_hash(user.password, password):
    return jsonify({'message': 'Invalid credentials!'}), 401
  access_token = create_access_token(identity=str(user.id))
  cache.clear()
  return jsonify({'access_token': access_token, 'role': user.role}), 200

@bp.route('/register', methods=['POST'])
def register():
  data = request.get_json()
  email = data.get('email')
  fullname = data.get('fullname').title()
  hashed_password = generate_password_hash(data.get('password'))
  if User.query.filter_by(email=email).first():
    return jsonify({'message': 'Email already taken!'}), 400
  user = User(email=email, fullname=fullname, password=hashed_password)
  db.session.add(user)
  db.session.commit()
  return jsonify({'message': 'User created successfully.'}), 200

# Admin Routes

def admin_required(fn):
  @wraps(fn)
  @jwt_required()
  def wrapper(*args, **kwargs):
    user = User.query.get(int(get_jwt_identity()))
    if not user.role == 'admin':
      return jsonify({'message': 'Not an admin!'}), 403
    return fn(*args, **kwargs)
  return wrapper

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
@cache.cached(timeout=30)
def admin_dashboard():
  now = datetime.now().isoformat()
  doctors = User.query.filter_by(role='doctor').all()
  patients = User.query.filter_by(role='patient').all()
  appointments = Appointment.query.filter_by(status='booked').all()
  doctors_data = [{'id': doctor.id, 'email': doctor.email, 'fullname': doctor.fullname, 'department': doctor.department_ref.name} for doctor in doctors]
  patients_data = [{'id': patient.id, 'email': patient.email, 'fullname': patient.fullname} for patient in patients]
  appointments_data = [{'id': appointment.id, 'patientId': appointment.patient_id, 'patient': appointment.patient.fullname, 'doctorId': appointment.doctor_id, 'doctor': appointment.doctor.fullname, 'department': appointment.doctor.department_ref.name, 'date': appointment.date, 'time': appointment.time} for appointment in appointments]
  return jsonify({'doctors':doctors_data, 'patients': patients_data, 'appointments': appointments_data, 'cachedAt': now}), 200

@admin_bp.route('/dashboard/<int:appointment_id>', methods=['PATCH'])
@admin_required
def admin_cancel_appointment(appointment_id):
  appointment = Appointment.query.get(appointment_id)
  if not appointment:
    return jsonify({'message': 'Appointment not found!'}), 404
  data = request.get_json()
  appointment.status = data.get('status')
  appointment.cancelled_by = 'admin'
  entry = History.query.filter_by(appointment_id=appointment_id).first()
  entry.status = 'cancelled'
  entry.cancelled_by = 'admin'
  db.session.commit()
  cache.clear()
  return jsonify({'message': 'Appointment cancelled.'}), 200

@admin_bp.route('/add/department', methods=['GET', 'POST'])
@admin_required
def add_department():
  if request.method == 'POST':
    data = request.get_json()
    name = data.get('name').title()
    description = data.get('description')
    if Department.query.filter_by(name=name).first():
      return jsonify({'message': 'Department already exists!'}), 400
    department = Department(name=name, description=description)
    db.session.add(department)
    db.session.commit()
    return jsonify({'message': 'Department added successfully.'}), 200
  departments = Department.query.all()
  departments_data = [{'id': department.id, 'name': department.name, 'description': department.description} for department in departments]
  return jsonify(departments=departments_data)

@admin_bp.route('/edit/department/<int:department_id>', methods=['GET'])
@admin_required
def edit_department_get(department_id):
  department = Department.query.get(department_id)
  department_details = {'id': department.id, 'name': department.name, 'description': department.description, 'doctors': [{'doctorId': doctor.id, 'doctorName': doctor.fullname} for doctor in department.doctor_registered]}
  return jsonify({'departmentDetails': department_details}), 200

@admin_bp.route('/edit/department/<int:department_id>', methods=['POST'])
@admin_required
def edit_department_post(department_id):
  department = Department.query.get(department_id)
  data = request.get_json()
  if not any(data.values()):
    return jsonify({'message': 'All fields are empty!'}), 400
  if data.get('name'):
    is_department = Department.query.filter_by(name=data.get('name').title()).first()
    if is_department:
      return jsonify({'message': 'Department with that name already exists!'}), 400
    department.name = data.get('name').title()
  if data.get('description'):
    department.description = data.get('description')
  db.session.commit()
  return jsonify({'message': 'Department updated successfully.'}), 200

@admin_bp.route('/edit/department/<int:department_id>', methods=['DELETE'])
@admin_required
def edit_department_delete(department_id):
  department = Department.query.get(department_id)
  if not department:
    return jsonify({'message': 'Department not found!'}), 404
  if User.query.filter_by(department_id=department.id).first():
    return jsonify({'message': 'Department contains 1 or more doctors!'}), 400
  db.session.delete(department)
  db.session.commit()
  return jsonify({'message': 'Department deleted successfully.'}), 200

@admin_bp.route('/add/doctor', methods=['GET'])
@admin_required
def add_doctor_get():
  departments = Department.query.all()
  department_data = [{'id': department.id, 'name': department.name} for department in departments]
  return jsonify({'departments': department_data}), 200

@admin_bp.route('/add/doctor', methods=['POST'])
@admin_required
def add_doctor():
  data = request.get_json()
  email = data.get('email')
  fullname = data.get('fullname').title()
  hashed_password = generate_password_hash(data.get('password'))
  department = Department.query.filter_by(name = data.get('department').title()).first()
  experience = data.get('experience').capitalize()
  about = data.get('about').capitalize()
  if not department:
    return jsonify({'message': f"{data.get('department')} department not found!"}), 400
  if User.query.filter_by(email=email).first():
    return jsonify({'message': 'Doctor with that email already exists!'}), 400
  doctor = User(email=email, fullname=fullname, password=hashed_password, role='doctor', department_id=department.id)
  doctor_profile = DoctorProfile(user_ref=doctor, fullname=fullname, department=department.name, experience=experience, about=about)
  db.session.add_all([doctor, doctor_profile])
  db.session.commit()
  cache.clear()
  return jsonify({'message': 'Doctor added successfully.'}), 200

@admin_bp.route('/edit/user/<int:user_id>', methods=['GET'])
@admin_required
def edit_user_get(user_id):
  user = User.query.get(user_id)
  if user.role == 'doctor':
    user_details = {'id': user.id, 'email': user.email, 'fullname': user.fullname, 'role': user.role, 'department': user.department_ref.name}
    alldepartments = Department.query.all()
    departments = [{'id': department.id, 'name': department.name} for department in alldepartments]
    doctor_profile = DoctorProfile.query.filter_by(doctor_id=user_id).first()
    extra_details = {'experience': doctor_profile.experience, 'about': doctor_profile.about}
    return jsonify({'userDetails': user_details, 'extraDetails': extra_details, 'departments': departments}), 200
  else:
    user_details = {'id': user.id, 'email': user.email, 'fullname': user.fullname, 'role': user.role}
    return jsonify({'userDetails': user_details}), 200
  
@admin_bp.route('/edit/user/<int:user_id>', methods=['POST'])
@admin_required
def edit_user_post(user_id):
  user = User.query.get(user_id)
  data = request.get_json()
  if user.role == 'doctor':
    doctor_profile = DoctorProfile.query.filter_by(doctor_id=user_id).first()
    if not any(data.values()):
      return jsonify({'message': 'All fields are empty!'}), 400
    if data.get('email'):
      email = User.query.filter_by(email=data.get('email')).first()
      if email:
        return jsonify({'message': 'Another user with email already exists!'}), 400
      user.email = data.get('email')
    if data.get('fullname'):
      entries = History.query.filter_by(doctor_id=user_id).all()
      for entry in entries:
        entry.doctor = data.get('fullname').title()
      user.fullname = data.get('fullname').title()
      doctor_profile.fullname = data.get('fullname').title()
    if data.get('department'):
      department = Department.query.filter_by(name=data.get('department')).first()
      user.department_id = department.id
      doctor_profile.department = department.name
    if data.get('experience'):
      doctor_profile.experience = data.get('experience').capitalize()
    if data.get('about'):
      doctor_profile.about = data.get('about').capitalize()
    db.session.commit()
  else:
    if data.get('fullname'):
      entries = History.query.filter_by(patient_id=user_id).all()
      for entry in entries:
        entry.patient = data.get('fullname').title()
      user.fullname = data.get('fullname').title()
    db.session.commit()
  return jsonify({'message': 'User updated successfully.'}), 200
  
@admin_bp.route('/edit/user/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
  user = User.query.get(user_id)
  if not user:
    return jsonify({'message': 'User not found!'}), 404
  appointment = Appointment.query.filter((Appointment.patient_id==user_id)|(Appointment.doctor_id==user_id), Appointment.status=='booked').first()
  if appointment:
    return jsonify({'message': 'Cannot delete user when unfinished appointment exists!'}), 403
  appointments = Appointment.query.filter((Appointment.doctor_id==user_id)|(Appointment.patient_id==user_id)).all()
  for a in appointments:
    db.session.delete(a)
  db.session.delete(user)
  db.session.commit()
  cache.clear()
  return jsonify({'message': 'User deleted.'}), 200

@admin_bp.route('/doctor/availability/<int:doctor_id>', methods=['GET'])
@admin_required
def admin_availability_get(doctor_id):
  today = datetime.now().date()
  slots_ref = {'slot1': '07 to 11 AM', 'slot2': '04 to 08 PM'}
  availability_list = []
  for i in range(7):
    day = today + timedelta(days=i)
    for slot_key, slot_time in slots_ref.items():
      availability_list.append({'date': str(day), 'slot': slot_key, 'time': slot_time, 'is_available': False, 'limit': 3})
  records = Availability.query.filter(Availability.doctor_id == doctor_id, Availability.date >= today, Availability.date <= today + timedelta(days=6)).all()
  record_map = {}
  for record in records:
    key = f"{str(record.date)}_{record.slot}"
    record_map[key] = record
  for item in availability_list:
    key = f"{item['date']}_{item['slot']}"
    if key in record_map:
      item['is_available'] = record_map[key].is_available
      item['limit'] = record_map[key].limit
  return jsonify({'availabilityData': availability_list}), 200

@admin_bp.route('/doctor/availability/<int:doctor_id>', methods=['POST'])
@admin_required
def admin_availability_post(doctor_id):
  data = request.get_json()
  for item in data:
    date = datetime.strptime(item['date'], '%Y-%m-%d').date()
    slot = item['slot']
    is_available = item['is_available']
    limit = item['limit']
    record = Availability.query.filter_by(doctor_id=doctor_id, date=date, slot=slot).first()
    if record:
      record.is_available = is_available
      record.limit = limit
    else:
      new_record = Availability(doctor_id=doctor_id, date=date, slot=slot, is_available=is_available, limit=limit)
      db.session.add(new_record)
  db.session.commit()
  return jsonify({'message': 'Availability saved.'}), 200

@admin_bp.route('/requests', methods=['GET'])
@admin_required
def change_requests():
  chrequests = RequestChange.query.all()
  chrequests_data = [{'id': chrequest.id, 'doctor_profile_id': chrequest.doctor_profile_id, 'doctor_id': chrequest.doc_profile_ref.user_ref.id, 'doctor_email': chrequest.doc_profile_ref.user_ref.email, 'doctor_fullname': chrequest.doc_profile_ref.fullname, 'change': chrequest.change, 'value': chrequest.value, 'notes': chrequest.notes} for chrequest in chrequests]
  return jsonify({'requestsData': chrequests_data}), 200

@admin_bp.route('/request/<int:request_id>', methods=['POST'])
@admin_required
def cancel_request(request_id):
  chrequest = RequestChange.query.get(request_id)
  doctor_id = chrequest.doc_profile_ref.user_ref.id
  data = request.get_json()
  reason = data.get('reason')
  change = chrequest.change
  reject_request.delay(doctor_id, reason, change)
  return jsonify({'message':'Request rejected successfully.'}), 200

@admin_bp.route('/request/<int:request_id>', methods=['DELETE'])
@admin_required
def clear_request(request_id):
  chrequest = RequestChange.query.get(request_id)
  db.session.delete(chrequest)
  db.session.commit()
  return jsonify({'message': 'Request Deleted.'}), 200

@admin_bp.route('/requests/count', methods=['GET'])
@admin_required
def requests_count():
  count = RequestChange.query.count()
  return jsonify({'count': count}), 200

@admin_bp.route('/users', methods=['GET'])
@admin_required
def all_users():
  users = User.query.all()
  users_data = [{'id': user.id, 'email': user.email, 'fullname': user.fullname, 'role': user.role} for user in users]
  return jsonify({'users': users_data}), 200

@admin_bp.route('/appointments', methods=['GET'])
@admin_required
def all_appointments():
  appointments = History.query.all()
  appointments_data = appointments_data = [{'id': appointment.id, 'patientId': appointment.patient_id, 'patient': appointment.patient, 'doctorId': appointment.doctor_id, 'doctor': appointment.doctor, 'department': appointment.department, 'date': appointment.date, 'time': appointment.time, 'status': appointment.status, 'cancelledBy': appointment.cancelled_by} for appointment in appointments]
  return jsonify({'appointments': appointments_data}), 200

# User Routes

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/doctor/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=30, key_prefix=lambda:f'dashboard_{get_jwt_identity()}')
def doctor_dashboard():
  now = datetime.now().isoformat()
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  if not user.role == 'doctor':
    return jsonify({'message': 'Not allowed!'}), 403
  booked_appointments = Appointment.query.filter_by(doctor_id=user_id, status='booked').all()
  booked_appointment_data = [{'id': appointment.id, 
                       'patientId': appointment.patient_id, 
                       'doctorId': appointment.doctor_id, 
                       'patient': appointment.patient.fullname, 
                       'date': appointment.date, 
                       'time': appointment.time} for appointment in booked_appointments]
  appointments = History.query.filter_by(doctor_id=user_id).all()
  assigned_patients = list({appointment.patient_id: 
                            {'patientId': appointment.patient_id, 
                             'doctorId': appointment.doctor_id, 
                             'name': appointment.patient} 
                             for appointment in appointments}.values())
  return jsonify({'fullname': user.fullname, 'doctorAppointments': booked_appointment_data, 'assignedPatients': assigned_patients, 'cachedAt': now}), 200

@user_bp.route('/doctor/dashboard/<int:appointment_id>', methods=['PATCH'])
@jwt_required()
def cancel_appointment_doctor(appointment_id):
  user_id = int(get_jwt_identity())
  appointment = Appointment.query.get(appointment_id)
  if not appointment.doctor_id == user_id:
    return jsonify({'message': 'Not allowed!'}), 403
  data = request.get_json()
  appointment.status = data.get('status')
  appointment.cancelled_by = 'doctor'
  entry = History.query.filter_by(appointment_id=appointment_id).first()
  entry.status = 'cancelled'
  entry.cancelled_by = 'doctor'
  db.session.commit()
  cache.clear()
  return jsonify({'message': 'Appointment cancelled.'}), 200

@user_bp.route('/doctor/availability', methods=['GET'])
@jwt_required()
def availability_get():
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  if not user.role == 'doctor':
    return jsonify({'message': 'Not allowed!'}), 403
  today = datetime.now().date()
  slots_ref = {'slot1': '07 to 11 AM', 'slot2': '04 to 08 PM'}
  availability_list = []
  for i in range(7):
    day = today + timedelta(days=i)
    for slot_key, slot_time in slots_ref.items():
      availability_list.append({'date': str(day), 'slot': slot_key, 'time': slot_time, 'is_available': False, 'limit': 3})
  records = Availability.query.filter(Availability.doctor_id == user_id, Availability.date >= today, Availability.date <= today + timedelta(days=6)).all()
  record_map = {}
  for record in records:
    key = f"{str(record.date)}_{record.slot}"
    record_map[key] = record
  for item in availability_list:
    key = f"{item['date']}_{item['slot']}"
    if key in record_map:
      item['is_available'] = record_map[key].is_available
      item['limit'] = record_map[key].limit
  return jsonify({'availabilityData': availability_list}), 200

@user_bp.route('/doctor/availability', methods=['POST'])
@jwt_required()
def availability_post():
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  if not user.role == 'doctor':
    return jsonify({'message': 'Not allowed!'}), 403
  data = request.get_json()
  for item in data:
    date = datetime.strptime(item['date'], '%Y-%m-%d').date()
    slot = item['slot']
    is_available = item['is_available']
    limit = item['limit']
    record = Availability.query.filter_by(doctor_id=user_id, date=date, slot=slot).first()
    if record:
      record.is_available = is_available
      record.limit = limit
    else:
      new_record = Availability(doctor_id=user_id, date=date, slot=slot, is_available=is_available, limit=limit)
      db.session.add(new_record)
  db.session.commit()
  return jsonify({'message': 'Availability saved.'}), 200

@user_bp.route('/doctor/treatment/appointment/<int:appointment_id>', methods=['GET'])
@jwt_required()
def treatment_get(appointment_id):
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  appointment = History.query.filter_by(appointment_id=appointment_id).first()
  if not user.role == 'doctor' or not appointment.doctor_id == user_id:
    return jsonify({'message': 'Not allowed!'}), 403
  patient = appointment.patient
  return jsonify({'patient': patient}), 200

@user_bp.route('/doctor/treatment/appointment/<int:appointment_id>', methods=['POST'])
@jwt_required()
def treatment_post(appointment_id):
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  appointment = Appointment.query.get(appointment_id)
  if not appointment:
    return jsonify({'message': 'Appointment not found!'}), 404
  if not user.role == 'doctor' or not appointment.doctor_id == user_id:
    return jsonify({'message': 'Not allowed!'}), 403
  if Treatment.query.filter_by(appointment_id=appointment_id).first():
    return jsonify({'message': 'Treatment already exists!'}), 400
  data = request.get_json()
  diagnosis = data.get('diagnosis')
  prescription = data.get('prescription')
  notes = data.get('notes')
  treatment = Treatment(appointment_id=appointment_id, diagnosis=diagnosis, prescription=prescription, notes=notes)
  appointment.status = 'completed'
  db.session.add(treatment)
  db.session.flush()
  entry = History.query.filter_by(appointment_id=appointment_id).first()
  entry.status = 'completed'
  entry.diagnosis = treatment.diagnosis
  entry.prescription = treatment.prescription
  entry.notes = treatment.notes
  db.session.commit()
  return jsonify({'message': 'Treatment added successfully.'}), 200

@user_bp.route('/update/treatment/appointment/<int:appointment_id>', methods=['GET'])
@jwt_required()
def update_treatment_get(appointment_id):
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  appointment = History.query.filter_by(appointment_id=appointment_id).first()
  if not user.role == 'doctor' or not appointment.doctor_id == user_id :
    return jsonify({'message': 'Not allowed'}), 403
  treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
  treatment_data = {'patient': appointment.patient,'id': treatment.id if treatment else '', 'diagnosis': appointment.diagnosis, 'prescription': appointment.prescription, 'notes': appointment.notes}
  return jsonify({'treatment': treatment_data}), 200

@user_bp.route('/update/treatment/appointment/<int:appointment_id>', methods=['POST'])
@jwt_required()
def update_treatment_post(appointment_id):
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  if not user.role == 'doctor':
    return jsonify({'message': 'Not allowed'}), 403
  treatment = Treatment.query.filter_by(appointment_id=appointment_id).first()
  entry = History.query.filter_by(appointment_id=appointment_id).first()
  data = request.get_json()
  if not any(data.values()):
    return jsonify({'message': 'All fields are empty!'}), 400
  if data.get('diagnosis'):
    treatment.diagnosis = data.get('diagnosis')
    entry.diagnosis = data.get('diagnosis')
  if data.get('prescription'):
    treatment.prescription = data.get('prescription')
    entry.prescription = data.get('prescription')
  if data.get('notes'):
    treatment.notes = data.get('notes')
    entry.notes = data.get('notes')
  db.session.commit()
  cache.clear()
  return jsonify({'message': 'Treatment updated.'}), 200

@user_bp.route('/doctor/profile/<int:user_id>', methods=['GET'])
@jwt_required()
def view_doctor(user_id):
  doctor = DoctorProfile.query.filter_by(doctor_id=user_id).first()
  if not doctor:
    return jsonify({'message': 'Doctor does not exist!'}), 404
  doctor_details = {'fullname': doctor.fullname, 'department': doctor.department, 'experience': doctor.experience, 'about': doctor.about}
  return jsonify({'doctorDetails': doctor_details}), 200

@user_bp.route('/update/info', methods=['GET'])
@jwt_required()
def update_info_get():
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  if user.role == 'doctor':
    user_details = {'id': user.id, 'email': user.email, 'fullname': user.fullname, 'role': user.role, 'department': user.department_ref.name}
    alldepartments = Department.query.all()
    departments = [{'id': department.id, 'name': department.name} for department in alldepartments]
    doctor_profile = DoctorProfile.query.filter_by(doctor_id=user_id).first()
    extra_details = {'experience': doctor_profile.experience, 'about': doctor_profile.about}
    return jsonify({'userDetails': user_details, 'extraDetails': extra_details, 'departments': departments}), 200
  else:
    user_details = {'id': user.id, 'email': user.email, 'fullname': user.fullname, 'role': user.role}
    return jsonify({'userDetails': user_details}), 200
  
@user_bp.route('/update/info', methods=['POST'])
@jwt_required()
def update_info_post():
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  data = request.get_json()
  if not any(data.values()):
    return jsonify({'message': 'All fields are empty!'}), 400
  if user.role == 'doctor':
    chrequest = RequestChange(doctor_profile_id=user.doctor.id, change=data.get('change'), value=data.get('value'), notes=data.get('notes'))
    db.session.add(chrequest)
    db.session.commit()
    return jsonify({'message': 'Update request sent.'}), 200
  else:
    entries = History.query.filter_by(patient_id=user_id).all()
    for entry in entries:
      entry.patient = data.get('fullname').title()
    fullname = data.get('fullname').title()
    user.fullname = fullname
    db.session.commit()
    return jsonify({'message': 'User updated.'}), 200
  
@user_bp.route('/patient/dashboard', methods=['GET'])
@jwt_required()
@cache.cached(timeout=30, key_prefix=lambda:f'dashboard_{get_jwt_identity()}')
def patient_dashboard():
  now = datetime.now().isoformat()
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  if not user.role == 'patient':
    return jsonify({'message': 'Not allowed!'}), 403
  departments = Department.query.all()
  departments_data = [{'id': department.id, 
                       'name': department.name} 
                       for department in departments]
  booked_appointments = Appointment.query.filter_by(patient_id=user_id, status='booked').all()
  booked_appointment_data = [{'id': appointment.id, 
                       'doctor': appointment.doctor.fullname, 
                       'department': appointment.doctor.department_ref.name ,
                       'date': appointment.date, 'time': appointment.time} 
                       for appointment in booked_appointments]
  appointments = History.query.filter_by(patient_id=user_id).all()
  assigned_doctors = list({appointment.doctor_id: {'doctorId': appointment.doctor_id, 'patientId': appointment.patient_id, 'name': appointment.doctor} for appointment in appointments}.values())
  return jsonify({'fullname': user.fullname, 'departments': departments_data, 'patientAppointments': booked_appointment_data, 'assignedDoctors': assigned_doctors, 'cachedAt': now}), 200

@user_bp.route('/patient/dashboard/<int:appointment_id>', methods=['PATCH'])
@jwt_required()
def cancel_appointment_patient(appointment_id):
  user_id = int(get_jwt_identity())
  appointment = Appointment.query.get(appointment_id)
  if not appointment.patient_id == user_id:
    return jsonify({'message': 'Not allowed!'}), 403
  data = request.get_json()
  appointment.status = data.get('status')
  appointment.cancelled_by = 'patient'
  entry = History.query.filter_by(appointment_id=appointment_id).first()
  entry.status = 'cancelled'
  entry.cancelled_by = 'patient'
  db.session.commit()
  cache.clear()
  return jsonify({'message': 'Appointment cancelled.'}), 200

@user_bp.route('/view/department/<int:department_id>')
@jwt_required()
def view_department(department_id):
  department = Department.query.filter_by(id=department_id).first()
  department_data = {'id': department.id, 'name': department.name, 'description': department.description, 'doctors': [{'id': doctor.id, 'fullname': doctor.fullname} for doctor in department.doctor_registered]}
  return jsonify({'department': department_data}), 200

@user_bp.route('/patient/book/doctor/<int:doctor_id>', methods=['GET'])
@jwt_required()
def book_doctor_get(doctor_id):
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  if not user.role == 'patient':
    return jsonify({'message': 'Not allowed!'}), 403
  if not User.query.get(doctor_id):
    return jsonify({'message': 'Doctor does not exist!'}), 404
  today = datetime.now().date()
  slots_ref = {'slot1': '07 to 11 AM', 'slot2': '04 to 08 PM'}
  availability_list = []
  for i in range(7):
    day = today + timedelta(days=i)
    for slot_key, slot_time in slots_ref.items():
      availability_list.append({'date': str(day), 'slot': slot_key, 'time': slot_time, 'available': False, 'seats_left': 0})
  records = Availability.query.filter(Availability.doctor_id == doctor_id, Availability.date >= today, Availability.date <= today + timedelta(days=6)).all()
  record_map = {}
  for record in records:
    key = f"{str(record.date)}_{record.slot}"
    record_map[key] = record
  for item in availability_list:
    key = f"{item['date']}_{item['slot']}"
    if key in record_map:
      record = record_map[key]
      booked_count = Appointment.query.filter_by(doctor_id=doctor_id, date=record.date, time=item['time'], status='booked').count()
      seats_left = max(record.limit - booked_count, 0)
      item['available'] = record.is_available and seats_left > 0
      item['seats_left'] = seats_left
  return jsonify({'availabilityData': availability_list}), 200

@user_bp.route('/patient/book/doctor/<int:doctor_id>', methods=['POST'])
@jwt_required()
def book_doctor_post(doctor_id):
  user_id = int(get_jwt_identity())
  user = User.query.get(user_id)
  doctor = User.query.get(doctor_id)
  if not user.role == 'patient':
    return jsonify({'message': 'Not allowed!'}), 403  
  data = request.get_json()
  date = datetime.strptime(data.get('date'), '%Y-%m-%d').date()
  slot = data.get('slot')
  time = data.get('time')
  record = Availability.query.filter_by(doctor_id=doctor_id, date=date, slot=slot).first()
  if not record or not record.is_available:
    return jsonify({'message': 'Slot unavailable'}), 400
  booked_count = Appointment.query.filter_by(doctor_id=doctor_id, date=date, time=time, status='booked').count()
  if booked_count >= record.limit:
    return jsonify({'message': 'Slot is full'}), 400
  is_booking = Appointment.query.filter_by(patient_id=user_id, doctor_id=doctor_id, status='booked').first()
  if is_booking:
    return jsonify({'message': 'Unfinished appointment exists!'}), 400
  booking = Appointment(patient_id=user_id, doctor_id=doctor_id, date=date, time=time)
  db.session.add(booking)
  db.session.flush()
  entry = History(appointment_id=booking.id, patient_id=user_id, patient=user.fullname, doctor_id=doctor_id, doctor=doctor.fullname, department=doctor.department_ref.name, date=date, time=time, status='booked')
  db.session.add(entry)
  db.session.commit()
  cache.clear()
  return jsonify({'message': 'Doctor booked successfully.'}), 200

@user_bp.route('/history/<int:patient_id>/<int:doctor_id>', methods=['GET'])
@jwt_required()
def patient_history_get(patient_id, doctor_id):
  user_id = int(get_jwt_identity())
  patient = User.query.get(patient_id)
  doctor = User.query.get(doctor_id)
  if not user_id == patient_id and not user_id == doctor_id and not user_id == 1:
    return jsonify({'message': 'Not allowed!'}), 403
  appointments = History.query.filter_by(patient_id=patient_id, doctor_id=doctor_id,status='completed').all()
  treatment_data = [{'appointmentId': appointment.id, 
                     'appointmentDate': appointment.date, 
                     'diagnosis': appointment.diagnosis, 
                     'prescription': appointment.prescription, 
                     'notes': appointment.notes} 
                     for appointment in appointments]
  name_data = {'patient': patient.fullname if patient else 'Deleted User', 'doctor': doctor.fullname if doctor else 'Deleted User'}
  return jsonify({'treatments': treatment_data, 'users': name_data}), 200

@user_bp.route('/departments', methods=['GET'])
@jwt_required()
def departments():
  all_departments = Department.query.all()
  departments_data = [{'id': department.id, 
                       'name': department.name} 
                       for department in all_departments]
  return jsonify({'departments': departments_data}), 200  

@user_bp.route('/export/patient/<int:patient_id>/<int:doctor_id>', methods=['POST'])
@jwt_required()
def export_csv(patient_id, doctor_id):
  user_id = int(get_jwt_identity())
  if not user_id == patient_id and not user_id == doctor_id and not user_id == 1:
    return jsonify({'message': 'Not allowed!'}), 403
  export_patient_csv.delay(patient_id, doctor_id)
  return jsonify({'message': 'Export started, check downloads section.'}), 200

@user_bp.route('/downloads', methods=['GET'])
@jwt_required()
def downloads():
  user_id = int(get_jwt_identity())
  downloads = Download.query.filter_by(patient_id=user_id).all()
  downloads_data = [{'id': download.id, 'filename': download.filename, 'createdAt': download.created_at, 'downloadStatus': download.status} for download in downloads]
  return jsonify({'downloads': downloads_data}), 200

@user_bp.route('/download/<int:download_id>', methods=['GET', 'DELETE'])
@jwt_required()
def download_file(download_id):
  download = Download.query.get(download_id)
  user_id = int(get_jwt_identity())
  if not user_id == download.patient_id:
    return jsonify({'message': 'Not allowed!'}), 403
  if request.method == 'DELETE':
    db.session.delete(download)
    db.session.commit()
    return jsonify({'message': 'Deleted.'}), 200
  file_path = os.path.join(current_app.root_path, 'exports', download.filename)
  return send_file(file_path, as_attachment=True)
