<script setup>

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router'; 
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const patientId = route.params.patientId;
const doctorId = route.params.doctorId;
const treatments = ref([]);
const users = ref({});
const role = ref('');

const getPatientHistory = async () => {
  try {
    const token = localStorage.getItem('token');
    role.value = localStorage.getItem('role');
    const response = await axios.get(`http://localhost:5000/user/history/${patientId}/${doctorId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    treatments.value = response.data.treatments;
    users.value = response.data.users;
  } catch (error) {
    console.error(`Error: ${error}.`);
    router.back();
  }
};

const goBack = () => {
  router.back()
};

const exportCsv = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post(`http://localhost:5000/user/export/patient/${patientId}/${doctorId}`, '', {
      headers: {
        'Authorization': `Bearer ${token}`
      },
    })
    alert(response.data.message);
  }
  catch (error) {
    console.error(`Error: ${error}.`);
  }
};

onMounted(getPatientHistory);
</script>

<template>

  <div v-if="role==='doctor'" class="container my-4">

    <h1>Patient History</h1> <br>
    <h5>Patient: {{ users.patient }}</h5>
    <h5>Doctor: {{ users.doctor }}</h5>
    <br>
    <p v-if="treatments.length === 0" class="text-muted">No history found.</p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Appointment ID</th>
          <th scope="col">Appointment Date</th>
          <th scope="col">Diagnosis</th>
          <th scope="col">Prescription</th>
          <th scope="col">Notes</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="treatment in treatments" :key="treatment.appointmentId">
          <td>{{ treatment.appointmentId }}</td>
          <td>{{ new Date(treatment.appointmentDate).toDateString() }}</td>
          <td>{{ treatment.diagnosis }}</td>
          <td>{{ treatment.prescription }}</td>
          <td>{{ treatment.notes }}</td>
          <td>
            <button @click="router.push(`/update/treatment/${treatment.appointmentId}`)" class="btn btn-primary">Update</button>
          </td>
        </tr>
      </tbody>
    </table>
    <button @click="goBack" class="btn btn-secondary">Back</button>
  </div>

  <div v-else class="container my-4">
    <div class="d-flex align-items-center justify-content-between">
      <h1>Patient History</h1>
      <button @click="exportCsv" class="btn btn-success d-flex justify-content-end">Export as CSV</button>
    </div>
    <br>
    <h5>Patient: {{ users.patient }}</h5>
    <h5>Doctor: {{ users.doctor }}</h5>
    <br>
    <p v-if="treatments.length === 0" class="text-muted">No history found.</p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Appointment ID</th>
          <th scope="col">Appointment Date</th>
          <th scope="col">Diagnosis</th>
          <th scope="col">Prescription</th>
          <th scope="col">Notes</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="treatment in treatments" :key="treatment.appointmentId">
          <td>{{ treatment.appointmentId }}</td>
          <td>{{ new Date(treatment.appointmentDate).toDateString() }}</td>
          <td>{{ treatment.diagnosis }}</td>
          <td>{{ treatment.prescription }}</td>
          <td>{{ treatment.notes }}</td>
        </tr>
      </tbody>
    </table>
    <button @click="goBack" class="btn btn-secondary">Back</button>
  </div>

</template>

<style scoped>

</style>