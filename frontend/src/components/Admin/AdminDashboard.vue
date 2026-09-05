<script setup>

import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const route = useRoute();
const doctors = ref([]);
const patients = ref([]);
const appointments = ref([]);

const searchQuery = ref('');
const lastRefreshed = ref('');

const searchDoctors = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return doctors.value.filter(doctor => {
    return (
      doctor.id.toString().includes(query) ||
      doctor.email.toLowerCase().includes(query) ||
      doctor.fullname.toLowerCase().includes(query) ||
      doctor.department.toLowerCase().includes(query)
    )
  })
});

const searchPatients = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return patients.value.filter(patient => {
    return (
      patient.id.toString().includes(query) ||
      patient.email.toLowerCase().includes(query) ||
      patient.fullname.toLowerCase().includes(query)
    )
  })
});

const refreshedText = computed(() => {
  const seconds = Math.floor((new Date() - new Date(lastRefreshed.value)) / 1000)
  return `Last updated ${seconds} seconds ago.`
});

const getDashboard = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5000/admin/dashboard', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    doctors.value = response.data.doctors;
    patients.value = response.data.patients;
    appointments.value = response.data.appointments;
    lastRefreshed.value = response.data.cachedAt;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const addDoctor = () => {
  router.push('/add/doctor');
}

const editUser = (id) => {
  router.push(`/edit/user/${id}`);
}

const cancelAppointment = async (id) => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.patch(`http://localhost:5000/admin/dashboard/${id}`, 
    {'status': 'cancelled'}, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    getDashboard();
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

onMounted(getDashboard);

</script>

<template>
  <div class="container my-4">
    <div class="d-flex align-items-center justify-content-between">
      <h1 class="fw-bold"> Admin Dashboard </h1>
      <div class="d-flex gap-1 ft-si">
        <i class="bi bi-arrow-repeat"></i>
        <p class="text-muted">{{ refreshedText }}</p>
      </div>
      <div class="border border-dark rounded">
        <input v-model="searchQuery" class="form-control" type="search" placeholder="Search" style="width:350px;">
      </div>
    </div>
    <br>
    <h3> 
      Registered Doctors 
      <button @click="addDoctor" class="btn btn-primary">Add</button>
    </h3>
    <p v-if="searchDoctors.length === 0" class="text-muted">
      No doctors registered.
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">User ID</th>
          <th scope="col">Email</th>
          <th scope="col">Full Name</th>
          <th scope="col">Department</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doctor in searchDoctors" :key="doctor.id">
          <th scope="row">{{ doctor.id }}</th>
          <td>{{ doctor.email }}</td>
          <td>{{ doctor.fullname }}</td>
          <td>{{ doctor.department }}</td>
          <td>
            <div class="d-flex gap-3">
              <button type="button" @click="editUser(doctor.id)" class="btn btn-info">Edit</button>
              <button type="button" @click="router.push(`/availability/${doctor.id}`)" class="btn btn-info">Availability</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <h3> Registered Patients </h3>
    <p v-if="searchPatients.length === 0" class="text-muted">
      No patients registered.
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">User ID</th>
          <th scope="col">Email</th>
          <th scope="col">Full Name</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="patient in searchPatients" :key="patient.id">
          <th scope="row">{{ patient.id }}</th>
          <td>{{ patient.email }}</td>
          <td>{{ patient.fullname }}</td>
          <td>
            <button @click="editUser(patient.id)" class="btn btn-info">Edit</button>
          </td>
        </tr>
      </tbody>
    </table>

    <h3> Upcoming Appointments </h3>
    <p v-if="appointments.length === 0" class="text-muted">No upcoming appointments.</p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Appointment ID</th>
          <th scope="col">Patient</th>
          <th scope="col">Doctor</th>
          <th scope="col">Department</th>
          <th scope="col">Date</th>
          <th scope="col">Time</th>
          <th scope="col">Patient History</th>
          <th scope="col">Manage</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="appointment in appointments" :key="appointment.id">
          <th scope="row">{{ appointment.id }}</th>
          <td>{{ appointment.patient }}</td>
          <td>{{ appointment.doctor }}</td>
          <td>{{ appointment.department }}</td>
          <td>{{ new Date(appointment.date).toDateString() }}</td>
          <td>{{ appointment.time }}</td>
          <td>
            <button @click="router.push(`/history/${appointment.patientId}/${appointment.doctorId}`)" class="btn btn-info">View</button>
          </td>
          <td>
            <button @click="cancelAppointment(appointment.id)" class="btn btn-danger">Cancel</button>
          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>

<style scoped>

.ft-si {
  font-size: 14px;
}

</style>