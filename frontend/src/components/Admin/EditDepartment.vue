<script setup>

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const departmentDetails = ref({});
const updateData = ref({
  name: '', description: '',
});

const getDepartmentInfo = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/admin/edit/department/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    departmentDetails.value = response.data.departmentDetails;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const updateDepartmentInfo = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(`http://localhost:5000/admin/edit/department/${route.params.id}`, updateData.value, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    alert(response.data.message);
    router.push('/add/department');
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
  }
};

const deleteDepartment = async () => {
  if (confirm("Are you sure you want to delete this department?")) {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.delete(`http://localhost:5000/admin/edit/department/${route.params.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      alert(response.data.message);
      router.push('/add/department');
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
  }
  } else {
    router.push('/add/department');
  }
};

onMounted(getDepartmentInfo);
</script>

<template>

  <div class="form-wrapper d-flex justify-content-center align-items-center">
    <div class="form-card card shadow-lg border-2">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Department Info</h1>
    
        <form @submit.prevent="updateDepartmentInfo">

          <div class="mb-3">
            <label for="exampleInputId" class="form-label">Department ID</label>
            <h5>{{ departmentDetails.id }}</h5>
          </div>

          <div class="mb-3">
            <label for="exampleInputDepartmentName" class="form-label">Department Name</label>
            <h5>{{ departmentDetails.name }}</h5>
            <input v-model="updateData.name" type="text" class="form-control" id="exampleInputDepartmentName" placeholder="New Department Name">
          </div>

          <div class="mb-3">
            <label for="exampleInputDepartmentDescription" class="form-label">Department Description</label>
            <h5>{{ departmentDetails.description}}</h5>
            <input v-model="updateData.description" type="text" class="form-control" id="exampleInputDepartmentDescription" placeholder="New Department Description">
          </div>

           <div class="mb-3">
            <label for="exampleInputDoctors" class="form-label">Doctors Registered</label>
            <div v-if="departmentDetails.doctors?.length">
              <p v-for="doctor in departmentDetails.doctors" :key="doctor.doctorId">
                ID: {{ doctor.doctorId }}, Name: {{ doctor.doctorName}},
              </p>
            </div>
            <p v-else class="text-muted">No doctors registered.
              <router-link class="text-decoration-none" to="/add/doctor">Register now.</router-link>
            </p>
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Update</button>
            <button type="button" @click="deleteDepartment" class="btn btn-danger">Delete</button>
            <button @click="router.push('/add/department')" class="btn btn-secondary">
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
  max-width: 500px;
  border-radius: 15px;
}

</style>