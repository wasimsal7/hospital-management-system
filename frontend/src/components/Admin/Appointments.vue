<script setup>

import { onMounted, ref, computed } from 'vue';
import axios from 'axios';

const appointments = ref([]);

const searchQuery = ref('')

const searchAppointments = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return appointments.value.filter(appointment => {
    return (
      appointment.id.toString().includes(query) ||
      appointment.patient.toLowerCase().includes(query) ||
      appointment.doctor.toLowerCase().includes(query) ||
      appointment.department.toLowerCase().includes(query) ||
      appointment.date.toLowerCase().includes(query) ||
      appointment.status.toLowerCase().includes(query)
    )
  })
});

const getAppointments = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/admin/appointments`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    appointments.value = response.data.appointments;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

onMounted(getAppointments);
</script>

<template>

  <div class="container my-4">
    <div class="d-flex align-items-center justify-content-between">
      <h1 class="fw-bold"> All Appointments </h1>
      <div class="border border-dark rounded">
        <input v-model="searchQuery" class="form-control" type="search" placeholder="Search" style="width:350px;">
      </div>
    </div>
    <br>
    <p v-if="searchAppointments.length === 0" class="text-muted">
      No appointments found.
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Appointment ID</th>
          <th scope="col">Patient ID</th>
          <th scope="col">Patient</th>
          <th scope="col">Doctor ID</th>
          <th scope="col">Doctor</th>
          <th scope="col">Department</th>
          <th scope="col">Date</th>
          <th scope="col">Time</th>
          <th scope="col">Status</th>
          <th scope="col">Cancelled By</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="appointment in searchAppointments" :key="appointment.id">
          <th scope="row">{{ appointment.id }}</th>
          <td>{{ appointment.patientId }}</td>
          <td>{{ appointment.patient }}</td>
          <td>{{ appointment.doctorId }}</td>
          <td>{{ appointment.doctor }}</td>
          <td>{{ appointment.department }}</td>
          <td>{{ new Date(appointment.date).toDateString() }}</td>
          <td>{{ appointment.time }}</td>
          <td>{{ appointment.status }}</td>
          <td>{{ appointment.cancelledBy }}</td>
        </tr>
      </tbody>
    </table>
  </div>

</template>

<style scoped>

</style>