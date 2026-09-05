<script setup>

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const patient = ref('');

const formData = ref({
  diagnosis: '', prescription: '', notes: '',
});

const getDetails = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/user/doctor/treatment/appointment/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    patient.value = response.data.patient;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const addTreatment = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(`http://localhost:5000/user/doctor/treatment/appointment/${route.params.id}`, formData.value, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    alert(response.data.message);
    router.push('/doctor/dashboard');
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
  }
};

onMounted(getDetails);
</script>

<template>

  <div class="form-wrapper d-flex justify-content-center align-items-center">
    <div class="form-card card shadow-lg border-2">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Treatment</h1>
    
        <form @submit.prevent="addTreatment">

          <div class="mb-3">
            <label for="exampleInputPatient" class="form-label">Patient</label>
            <h5>{{ patient }}</h5>
          </div>

          <div class="mb-3">
            <label for="exampleInputDiagnosis" class="form-label">Diagnosis</label>
            <input v-model="formData.diagnosis" type="text" class="form-control" id="exampleInputDiagnosis" required>
          </div>

          <div class="mb-3">
            <label for="exampleInputPrescription" class="form-label">Prescription</label>
            <input v-model="formData.prescription" type="text" class="form-control" id="exampleInputPrescription" required>
          </div>

          <div class="mb-3">
            <label for="exampleInputNotes" class="form-label">Notes</label>
            <input v-model="formData.notes" type="text" class="form-control" id="exampleInputNotes" required>
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Add</button>
            <button type="button" @click="router.push('/doctor/dashboard')" class="btn btn-secondary">
            Cancel
            </button>
          </div>

        </form>

      </div>
    </div>
  </div>

</template>

<style scoped>

.form-wrapper {
  min-height: 80vh;
}

.form-card {
  width: 100%;
  max-width: 450px;
  border-radius: 15px;
}

</style>