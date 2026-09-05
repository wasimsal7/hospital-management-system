<script setup>

import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const departments = ref([]);

const searchQuery = ref('');

const searchDepartments = computed(() => {
  return departments.value.filter(department => 
    department.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
});

const getDashboard = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5000/user/departments', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    departments.value = response.data.departments;
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
  }
};

const viewDepartment = (id) => {
  router.push(`/view/department/${id}`);
}

onMounted(getDashboard);

</script>

<template>

  <div class="container my-4">
    <div class="d-flex align-items-center justify-content-between">
      <h1> Departments </h1>
      <form class="border border-dark rounded">
        <input v-model="searchQuery" class="form-control" type="search" placeholder="Search" style="width:350px;">
      </form>
    </div>
    <br>
    <p v-if="searchDepartments.length === 0" class="text-muted">
      No departments found.
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Department</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="department in searchDepartments" :key="department.id">
          <th scope="row">{{ department.name }}</th>
          <td>
            <button @click="viewDepartment(department.id)" class="btn btn-info">View</button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

</template>

<style scoped>

</style>