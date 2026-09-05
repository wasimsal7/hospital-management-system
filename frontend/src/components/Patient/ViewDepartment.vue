<script setup>

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router'; 
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const department = ref({
  doctors: [],
});

const getDepartmentInfo = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/user/view/department/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    department.value = response.data.department;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const bookDoctor = async (id) => {
  router.push(`/book/doctor/${id}`);
}

onMounted(getDepartmentInfo);
</script>

<template>

  <div class="container my-4">

    <h1>{{ department.name }}</h1>
    <br>
    <h3>Description: </h3>
    <h6>{{ department.description }}</h6>
    <br>
    <h3>Doctors: </h3>
    <p v-if="department.doctors.length === 0" class="text-muted">No doctors found.</p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Doctors</th>
          <th scope="col">Book Doctor</th>
          <th scope="col">About Doctor</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="doctor in department.doctors" :key="doctor.id">
          <td>{{ doctor.fullname }}</td>
          <td>
            <button @click="bookDoctor(doctor.id)" class="btn btn-primary">Book</button>
          </td>
          <td>
            <button @click="router.push(`/doctor/profile/${doctor.id}`)" class="btn btn-info">View</button>
          </td>
        </tr>
      </tbody>
    </table>
    <button @click="router.back()" class="btn btn-secondary">Back</button>

  </div>

</template>

<style scoped>

</style>