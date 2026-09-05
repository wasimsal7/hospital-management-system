<script setup>

import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const formData = ref({
  email: '', password: '',
});

const router = useRouter();

const login = async () => {
  try {
    const response = await axios.post('http://localhost:5000/login', formData.value);
    localStorage.setItem('token', response.data.access_token);
    localStorage.setItem('role', response.data.role);
    const role = localStorage.getItem('role');
    alert('Login Successful.');
    if (role === 'admin') {
      router.push('/admin/dashboard');
    } else if (role === 'doctor') {
      router.push('/doctor/dashboard');
    } else {
      router.push('/patient/dashboard');
    }
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error.response.data.message);
    formData.value = {email: '', password: ''};
  }
};

onMounted(() => {
  if (localStorage.getItem('token')) {
    router.push(`/${localStorage.getItem('role')}/dashboard`);
  }
});
</script>

<template>

  <div class="login-wrapper d-flex justify-content-center align-items-center">
    <div class="login-card card shadow-lg border-0">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Login</h1>
    
        <form @submit.prevent="login">

          <div class="mb-3">
            <label for="exampleInputeEmail1" class="form-label">Email</label>
            <input v-model="formData.email" type="email" class="form-control" id="exampleInputEmail1" required>
          </div>

          <div class="mb-3">
            <label for="exampleInputPassword1" class="form-label">Password</label>
            <input v-model="formData.password" type="password" class="form-control" id="exampleInputPassword1" required>
          </div>

          <button type="submit" class="btn btn-primary">Login</button>

        </form>

        <p class="text-muted mt-5 mb-0"> Don't have an account?
          <router-link to="/register" class="text-decoration-none">Register here.</router-link>
        </p>
      
      </div>
    </div>
  </div>

</template>

<style scoped>

.login-wrapper {
  min-height: 85vh;
}

.login-card {
  width: 100%;
  max-width: 450px;
  border-radius: 15px;
}

</style>