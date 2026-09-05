<script setup>

import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const fullname = ref('');
const departments = ref([]);
const patientAppointments = ref([]);
const assignedDoctors = ref([]);
const lastRefreshed = ref('');

const searchQuery = ref('');

const searchAssignedDoctors = computed(() => {
  return assignedDoctors.value?.filter(doctor => 
    doctor.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
});

const searchPatientAppointments = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return patientAppointments.value.filter(appointment => {
    return (
      appointment.doctor.toLowerCase().includes(query) ||
      appointment.department.toLowerCase().includes(query) ||
      appointment.date.toLowerCase().includes(query)
    )
  })
});

const refreshedText = computed(() => {
  const seconds = Math.floor((new Date() - new Date(lastRefreshed.value)) / 1000)
  return `Last updated ${seconds} seconds ago.`
})

const getDashboard = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5000/user/patient/dashboard', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    fullname.value = response.data.fullname;
    departments.value = response.data.departments;
    patientAppointments.value = response.data.patientAppointments;
    assignedDoctors.value = response.data.assignedDoctors;
    lastRefreshed.value = response.data.cachedAt;
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
  }
};

const cancelAppointment = async (id) => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.patch(`http://localhost:5000/user/patient/dashboard/${id}`,
    {'status': 'cancelled'}, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    getDashboard();
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
  }
}

const patientHistory = (patientId, doctorId) => {
  router.push(`/history/${patientId}/${doctorId}`);
}

onMounted(getDashboard);

</script>

<template>

  <div class="container my-4">
    <div class="d-flex align-items-center justify-content-between">
      <h1>Welcome, {{ fullname }}.</h1>
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
    <p v-if="patientAppointments.length === 0" class="text-muted">No upcoming appointments. <router-link to="/departments" class="text-decoration-none">Book now.</router-link> </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Appointment ID</th>
          <th scope="col">Doctor Name</th>
          <th scope="col">Department</th>
          <th scope="col">Date</th>
          <th scope="col">Time</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="appointment in searchPatientAppointments" :key="appointment.id">
          <th scope="row">{{ appointment.id }}</th>
          <td>{{ appointment.doctor }}</td>
          <td>{{ appointment.department }}</td>
          <td>{{ new Date(appointment.date).toDateString() }}</td>
          <td>{{ appointment.time }}</td>
          <td>
            <button @click="cancelAppointment(appointment.id)" class="btn btn-danger">Cancel</button>
          </td>
        </tr>
      </tbody>
    </table>
    <br>
    <h3>Assigned Doctors</h3>
    <p v-if="searchAssignedDoctors.length === 0" class="text-muted">
      No assigned doctors. <router-link to="/departments" class="text-decoration-none">Book now.</router-link>
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Doctor Name</th>
          <th scope="col">Patient History</th>
          <th scope="col">About Doctor</th>
          <th scope="col">Book New Appointment</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doctor in searchAssignedDoctors" :key="doctor.id">
          <td>{{ doctor.name }}</td>
          <td>
            <button @click="patientHistory(doctor.patientId, doctor.doctorId)" class="btn btn-info">View</button>
          </td>
          <td>
            <button @click="router.push(`/doctor/profile/${doctor.doctorId}`)" class="btn btn-info">View</button>
          </td>
          <td>
            <button @click="router.push(`/book/doctor/${doctor.doctorId}`)" class="btn btn-primary">Book</button>
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