<script setup>

import { useRouter, useRoute } from 'vue-router';
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';

const loggedIn = ref(false);
const role = ref('');
const router = useRouter();
const route = useRoute();
const requestCount = ref(0);

const getRequestCount = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5000/admin/requests/count', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    requestCount.value = response.data.count;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const logout = () => {
  localStorage.clear();
  router.push('/login');
};

watch(route, () => {
  loggedIn.value = !!localStorage.getItem('token');
  role.value = localStorage.getItem('role');
  if (role.value === 'admin') {
    getRequestCount();
  }
}, {immediate: true});

</script>

<template>

  <div v-if="loggedIn">

    <div v-if="role==='admin'">

      <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid d-flex align-items-center py-3">

          <div class="d-flex align-items-center gap-5">
            <span class="navbar-brand mb-0 h1 ms-4" style="color:red;">Admin</span>
            <router-link class="nav-link text-light" to="/admin/dashboard">Dashboard</router-link>
            <router-link class="nav-link text-light" to="/add/department">Departments</router-link>
            <router-link class="nav-link text-light" to="/users">Users</router-link>
            <router-link class="nav-link text-light" to="/appointments">Appointments</router-link>
          </div>
          
          <div class="d-flex align-items-center gap-5 me-5">
            <router-link class="inbox fs-3" to="/requests">
              <i :class="requestCount > 0 ? 'bi bi-envelope-exclamation' : 'bi bi-envelope'"></i>
            </router-link>
            <button @click="logout" class="btn btn-outline-danger btn-sm">Logout</button>
          </div>

        </div>
      </nav>

    </div>
    
    <div v-else-if="role==='doctor'">

      <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid d-flex align-items-center py-3">

          <div class="d-flex align-items-center gap-5">
            <span class="navbar-brand mb-0 h1 ms-4">Doctor</span>
            <router-link class="nav-link text-light" to="/doctor/dashboard">Dashboard</router-link>
            <router-link class="nav-link text-light" to="/doctor/availability">Availability</router-link>
          </div>

          <div class="d-flex align-items-center gap-5 me-5">
            <router-link class="inbox fs-3" to="/update/info">
              <i class="bi bi-person-fill"></i>
            </router-link>
            <button @click="logout" class="btn btn-outline-danger btn-sm me-5">Logout</button>
          </div>

        </div>
      </nav>

    </div>

    <div v-else>

      <nav class="navbar navbar-dark bg-dark">
        <div class="container-fluid d-flex align-items-center py-3">

          <div class="d-flex align-items-center gap-5">
            <span class="navbar-brand mb-0 h1 ms-4">Patient</span>
            <router-link class="nav-link text-light" to="/patient/dashboard">Dashboard</router-link>
            <router-link class="nav-link text-light" to="/departments">Departments</router-link>
            <router-link class="nav-link text-light" to="/downloads">Downloads</router-link>
          </div>

          <div class="d-flex align-items-center gap-5 me-5">
            <router-link class="inbox fs-3" to="/update/info">
              <i class="bi bi-person-fill"></i>
            </router-link>
            <button @click="logout" class="btn btn-outline-danger btn-sm me-5">Logout</button>
          </div>

        </div>
      </nav>

    </div>
  
  </div>

</template>

<style scoped>

.inbox {
 color:aliceblue;
}

.inbox :hover {
  color:aquamarine;
  transition: 0.5s;
}

</style>