<script setup>

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const treatment = ref({});

const updateData = ref({
  diagnosis: '', prescription: '', notes: '',
});

const getDetails = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/user/update/treatment/appointment/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    treatment.value = response.data.treatment;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const addTreatment = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(`http://localhost:5000/user/update/treatment/appointment/${route.params.id}`, updateData.value, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    alert(response.data.message);
    router.back();
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
  }
};

onMounted(getDetails);
</script>

<template>

  <div class="form-wrapper d-flex justify-content-center align-items-center">
    <div class="form-card card shadow-lg border-2 mt-2">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Treatment</h1>
    
        <form @submit.prevent="addTreatment">

          <div class="mb-4">
            <label for="exampleInputPatient" class="form-label">Patient</label>
            <h5>{{ treatment.patient }}</h5>
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Diagnosis: {{ treatment.diagnosis }}</p>
            <input v-model="updateData.diagnosis" type="text" class="form-control" id="exampleInputDiagnosis" placeholder="New Diagnosis">
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Prescription: {{ treatment.prescription }}</p>
            <input v-model="updateData.prescription" type="text" class="form-control" id="exampleInputPrescription" placeholder="New Prescription">
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Notes: {{ treatment.notes }}</p>
            <input v-model="updateData.notes" type="text" class="form-control" id="exampleInputNotes" placeholder="New Notes">
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Update</button>
            <button type="button" @click="router.back()" class="btn btn-secondary">
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