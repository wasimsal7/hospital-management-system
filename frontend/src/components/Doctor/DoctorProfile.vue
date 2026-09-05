<script setup>

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router'; 
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const doctorId = route.params.id;
const doctorDetails = ref({});

const getDoctorProfile = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/user/doctor/profile/${doctorId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    doctorDetails.value = response.data.doctorDetails;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const goBack = () => {
  router.back()
};

onMounted(getDoctorProfile);
</script>

<template>

  <div class="form-wrapper d-flex justify-content-center align-items-center">
    <div class="form-card card shadow-lg border-0">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Doctor Profile</h1>

          <div class="mb-3">
            <label>Name</label>
            <h4 class="fw-semibold">Dr. {{ doctorDetails.fullname }}</h4>
          </div>

          <div class="mb-3">
            <label>Department</label>
            <h5 class="fw-medium">{{ doctorDetails.department }}</h5>
          </div>

          <div class="mb-3">
            <label>Experience</label>
            <h5 class="fw-medium">{{ doctorDetails.experience }}</h5>
          </div>

          <div class="mb-3">
            <label>About</label>
            <h6 class="fw-medium">{{ doctorDetails.about }}</h6>
          </div>

          <div class="d-flex gap-3 mt-4">
            <button @click="router.back()" class="btn btn-secondary">
              Back</button>
          </div>

      </div>
    </div>
  </div>

</template>

<style scoped>

.form-wrapper {
  min-height: 85vh;
}

.form-card {
  width: 100%;
  max-width: 450px;
  border-radius: 15px;
}

</style>