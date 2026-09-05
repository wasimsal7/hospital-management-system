<script setup>

import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const formData = ref({
  email: '', fullname: '', password: '', department: '', experience: '', about: '',
});

const departments = ref([]);

const getDepartments = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5000/admin/add/doctor', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    departments.value = response.data.departments;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const addDoctor = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post('http://localhost:5000/admin/add/doctor', formData.value, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    alert(response.data.message);
    router.push('/admin/dashboard');
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error.response.data.message);
  }
};

onMounted(getDepartments);

</script>

<template>

  <div class="form-wrapper d-flex justify-content-center align-items-center">
    <div class="form-card card shadow-lg border-2">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Create Doctor</h1>
    
        <form @submit.prevent="addDoctor">

          <div class="mb-4">
            <input v-model="formData.email" type="email" class="form-control" id="exampleInputEmail1" placeholder="Email Address" required>
          </div>

          <div class="mb-4">
            <input v-model="formData.fullname" type="text" class="form-control" id="exampleInputFullName1" placeholder="Full Name" required>
          </div>

          <div class="mb-4">
            <input v-model="formData.password" type="password" class="form-control" id="exampleInputPassword1" placeholder="Password" required>
          </div>

          <div class="mb-4">
            <select v-model="formData.department" class="form-select">
              <option value="">Select department</option>
              <option v-for="department in departments" :key="department.id" :value="department.name">
                {{ department.name }}
              </option>
            </select>
          </div>

          <div class="mb-4">
            <input v-model="formData.experience" type="text" class="form-control" id="exampleInputExperience" placeholder="Experience" required>
          </div>

          <div class="mb-4">
            <input v-model="formData.about" type="text" class="form-control" id="exampleInputAbout" placeholder="About" required>
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Add Doctor</button>
            <button @click="router.push('/admin/dashboard')" class="btn btn-secondary">
              Cancel</button>
          </div>

        </form>

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