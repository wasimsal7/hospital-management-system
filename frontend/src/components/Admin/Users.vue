<script setup>

import { onMounted, computed, ref } from 'vue';
import axios from 'axios';

const users = ref([]);
const searchQuery = ref('')

const searchUsers = computed(() => {
  const query = searchQuery.value.toLowerCase();
  return users.value.filter(user => {
    return (
      user.id.toString().includes(query) ||
      user.fullname.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query) ||
      user.role.toLowerCase().includes(query)
    )
  })
});

const getUsers = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/admin/users`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    users.value = response.data.users;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

onMounted(getUsers);
</script>

<template>

  <div class="container my-4">
    <div class="d-flex align-items-center justify-content-between">
      <h1 class="fw-bold"> All Users </h1>
      <div class="border border-dark rounded">
        <input v-model="searchQuery" class="form-control" type="search" placeholder="Search" style="width:350px;">
      </div>
    </div>
    <br>
    <p v-if="searchUsers.length === 0" class="text-muted">
      No users found.
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">User ID</th>
          <th scope="col">Email</th>
          <th scope="col">Full Name</th>
          <th scope="col">Role</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in searchUsers" :key="user.id">
          <th scope="row">{{ user.id }}</th>
          <td>{{ user.email }}</td>
          <td>{{ user.fullname }}</td>
          <td>{{ user.role }}</td>
        </tr>
      </tbody>
    </table>
  </div>

</template>

<style scoped>

</style>