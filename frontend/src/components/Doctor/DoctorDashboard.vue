<script setup>

import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const fullname = ref('');
const doctorAppointments = ref([]);
const assignedPatients = ref([]);
const searchQuery = ref('');
const lastRefreshed = ref('');

const searchAssignedPatients = computed(() => {
  return assignedPatients.value.filter(patient => 
    patient.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
});

const searchDoctorAppointments = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return doctorAppointments.value.filter(appointment => {
    return (
      appointment.patient.toLowerCase().includes(query) ||
      appointment.date.toLowerCase().includes(query) ||
      appointment.time.toLowerCase().includes(query)
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
    const response = await axios.get('http://localhost:5000/user/doctor/dashboard', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    fullname.value = response.data.fullname;
    doctorAppointments.value = response.data.doctorAppointments;
    assignedPatients.value = response.data.assignedPatients;
    lastRefreshed.value = response.data.cachedAt;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const cancelAppointment = async (id) => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.patch(`http://localhost:5000/user/doctor/dashboard/${id}`, {'status': 'cancelled'}, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    getDashboard();
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const treatment = (id) => {
  router.push(`/doctor/treatment/${id}`);
}

const patientHistory = (patientId, doctorId) => {
  router.push(`/history/${patientId}/${doctorId}`);
}

onMounted(getDashboard);

</script>

<template>

  <div class="container my-4">
    <div class="d-flex align-items-center justify-content-between">
      <h1>Welcome, Dr. {{ fullname }}.</h1>
      <div class="d-flex gap-1 ft-si">
        <i class="bi bi-arrow-repeat"></i>
        <p class="text-muted">{{ refreshedText }}</p>
      </div>
      <form class="border border-dark rounded">
        <input v-model="searchQuery" class="form-control" type="search" placeholder="Search" style="width:350px;">
      </form>
    </div>
    <br>
    <h3> Upcoming Appointments </h3>
    <p v-if="searchDoctorAppointments.length === 0" class="text-muted">
      No upcoming appointments.
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Appointment ID</th>
          <th scope="col">Patient Name</th>
          <th scope="col">Patient History</th>
          <th scope="col">Date</th>
          <th scope="col">Time</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="appointment in searchDoctorAppointments" :key="appointment.id">
          <th scope="row">{{ appointment.id }}</th>
          <td>{{ appointment.patient }}</td>
          <td>
            <button @click="patientHistory(appointment.patientId, appointment.doctorId)" class="btn btn-info">View</button>
          </td>
          <td>{{ new Date(appointment.date).toDateString() }}</td>
          <td>{{ appointment.time }}</td>
          <td>
            <div class="d-flex gap-3 mt-0">
              <button @click="treatment(appointment.id)" class="btn btn-success">Mark as complete</button>
              <button @click="cancelAppointment(appointment.id)" class="btn btn-danger">Cancel</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <br>
    <h3>Assigned Patients</h3>
    <p v-if="searchAssignedPatients.length === 0" class="text-muted">No assigned patients.</p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Patient Name</th>
          <th scope="col">Patient History</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="patient in searchAssignedPatients" :key="patient.id">
          <td>{{ patient.name }}</td>
          <td>
            <button @click="patientHistory(patient.patientId, patient.doctorId)" class="btn btn-info">View</button>
          </td>
        </tr>
      </tbody>
    </table>
    <button @click="router.push('/doctor/availability')" class="btn btn-primary">Provide Availability</button>
  </div>

</template>

<style scoped>

.ft-si {
  font-size: 14px;
}

</style>