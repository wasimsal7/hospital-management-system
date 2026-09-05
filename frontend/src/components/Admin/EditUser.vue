<script setup>

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();
const userDetails = ref({});
const extraDetails = ref({});
const updateData = ref({
  email: '', fullname: '', department: '', experience: '', about: '',
});
const departments = ref([]);
const showMore = ref(false);

const getUserInfo = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/admin/edit/user/${route.params.id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    userDetails.value = response.data.userDetails;
    extraDetails.value = response.data.extraDetails;
    departments.value = response.data.departments;
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const updateUserInfo = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(`http://localhost:5000/admin/edit/user/${route.params.id}`, updateData.value, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    alert(response.data.message);
    router.push('/admin/dashboard')
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
  }
};

const deleteUser = async () => {
  if (confirm("Are you sure you want to delete this user?")) {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.delete(`http://localhost:5000/admin/edit/user/${route.params.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      router.push('/admin/dashboard');
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
  } else {
    router.push('/admin/dashboard');
  }
};

onMounted(getUserInfo);
</script>

<template>

  <div v-if="userDetails.role === 'doctor'" class="form-wrapper d-flex justify-content-center align-items-center mt-1">
    <div class="form-card card shadow-lg border-2">
      <div class="card-body p-4">
        <h1 class="fw-bold text-center mb-5">Doctor Info</h1>
        <form @submit.prevent="updateUserInfo">

          <div class="mb-3">
            <p class="fw-semibold text-muted">User ID : {{ userDetails.id }}</p>
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Email: {{ userDetails.email }} </p>
            <input v-model="updateData.email" type="email" class="form-control" id="exampleInputEmail1" placeholder="New Email">
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Full Name: {{ userDetails.fullname }}</p>
            <input v-model="updateData.fullname" type="text" class="form-control" id="exampleInputFullName" placeholder="New Full Name">
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Department: {{ userDetails.department }}</p>
            <select v-model="updateData.department" class="form-select">
              <option value="">Select new department</option>
              <option v-for="department in departments" :key="department.id" :value="department.name">
                {{ department.name }}
              </option>
            </select>
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Experience: {{ extraDetails.experience }}</p>
            <input v-model="updateData.experience" type="text" class="form-control" id="exampleInputExperience" placeholder="New Experience">
          </div>

          <div class="mb-3">
              <p class="fw-medium mb-1">About: {{ showMore ? extraDetails.about : extraDetails.about.slice(0, 30) + '...'}}
              <span @click="showMore=!showMore" class="show-more">{{showMore ? 'less' : 'more'}}</span>
                </p>
            <input v-model="updateData.about" type="text" class="form-control" id="exampleInputAbout" placeholder="New About">
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Update</button>
            <button type="button" @click="deleteUser" class="btn btn-danger">Delete</button>
            <button type="button" @click="router.back()" class="btn btn-secondary">
              Cancel</button>
          </div>

        </form>

      </div>
    </div>
  </div>

  <div v-else class="form-wrapper d-flex justify-content-center align-items-center">
    <div class="form-card card shadow-lg border-2">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Patient Info</h1>
    
        <form @submit.prevent="updateUserInfo">

          <div class="mb-3">
            <p class="fw-semibold text-muted">User ID : {{ userDetails.id }}</p>
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Email: {{ userDetails.email }} </p>
          </div>

          <div class="mb-4">
            <p class="fw-medium mb-1">Full Name: {{ userDetails.fullname }}</p>
            <input v-model="updateData.fullname" type="text" class="form-control" id="exampleInputFullName" placeholder="New Full Name">
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Update</button>
            <button type="button" @click="deleteUser" class="btn btn-danger">Delete</button>
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
  max-width: 500px;
  border-radius: 15px;
}

.show-more {
  color: blue;
  cursor: pointer;
}

</style>