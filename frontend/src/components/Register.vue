<script setup>

import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const formData = ref({
  email: '', fullname: '', password: '',
});

const register = async () => {
  try {
    const response = await axios.post('http://localhost:5000/register', formData.value)
    formData.value = {email: '', fullname: '', password: ''};
    alert(response.data.message);
    router.push('/login');
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error.response.data.message);
    formData.value = {email: '', fullname: '', password: ''};
  }
};

</script>

<template>

  <div class="registration-wrapper d-flex justify-content-center align-items-center">
    <div class="registration-card card shadow-lg border-0">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Register</h1>
    
        <form @submit.prevent="register">

          <div class="mb-3">
            <label for="exampleInputEmail1" class="form-label">Email address</label>
            <input v-model="formData.email" type="email" class="form-control" id="exampleInputEmail1" required>
          </div>

          <div class="mb-3">
            <label for="exampleInputFullName1" class="form-label">Full Name</label>
            <input v-model="formData.fullname" type="text" class="form-control" id="exampleInputFullName1" required>
          </div>

          <div class="mb-3">
            <label for="exampleInputPassword1" class="form-label">Password</label>
            <input v-model="formData.password" type="password" class="form-control" id="exampleInputPassword1" required>
          </div>

          <button type="submit" class="btn btn-primary">Register</button>

        </form>

        <p class="text-muted mt-5 mb-0"> Already have an account?
          <router-link to="/login" class="text-decoration-none">Login here.</router-link>
        </p>
      
      </div>
    </div>
  </div>

</template>

<style scoped>

.registration-wrapper {
  min-height: 85vh;
}

.registration-card {
  width: 100%;
  max-width: 450px;
  border-radius: 15px;
}

</style>