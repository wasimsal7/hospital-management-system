<script setup>

import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();

const formData = ref({
  name: '', description: '',
});

const departments = ref([]);

const showAddDepartment = ref(false);

const getDepartment = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5000/admin/add/department', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    departments.value = response.data.departments;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const addDepartment = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post('http://localhost:5000/admin/add/department', formData.value, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    alert(response.data.message);
    showAddDepartment.value = false;
    formData.value = {name: '', description: ''};
    getDepartment()
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error.response.data.message);
  }
};

const editDepartment = (id) => {
  router.push(`/edit/department/${id}`)
};

onMounted(getDepartment);

</script>

<template>

  <div v-if="!showAddDepartment" class="container my-4">
    <h3> Departments </h3>
    <p v-if="departments.length === 0" class="text-muted">
      No departments found.
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Department ID</th>
          <th scope="col">Department Name</th>
          <th scope="col">Description</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="department in departments" :key="department.id">
          <th scope="row">{{ department.id }}</th>
          <td>{{ department.name }}</td>
          <td>{{ department.description }}</td>
          <td>
            <button @click="editDepartment(department.id)" class="btn btn-info">Edit</button>
          </td>
        </tr>
      </tbody>
    </table>

    <button @click="showAddDepartment=true" class="btn btn-primary">
      Add Department
    </button>
  </div>

  <div v-else class="form-wrapper d-flex justify-content-center align-items-center">
    <div class="form-card card shadow-lg border-2">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Create Department</h1>
    
        <form @submit.prevent="addDepartment">

          <div class="mb-3">
            <label for="exampleInputName" class="form-label">Department</label>
            <input v-model="formData.name" type="text" class="form-control" id="exampleInputName" required>
          </div>

          <div class="mb-3">
            <label for="exampleInputDescription" class="form-label">Description</label>
            <input v-model="formData.description" type="text" class="form-control" id="exampleInputDescription" required>
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Add Department</button>
            <button type="button" @click="showAddDepartment=false" class="btn btn-secondary">
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
  min-height: 70vh;
}

.form-card {
  width: 100%;
  max-width: 450px;
  border-radius: 15px;
}

</style>