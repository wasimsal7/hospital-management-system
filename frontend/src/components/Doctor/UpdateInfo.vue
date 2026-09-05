<script setup>

import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const role = localStorage.getItem('role');
const route = useRoute();
const router = useRouter();
const userDetails = ref({});
const extraDetails = ref({});
const updateInfo = ref({
  change: '', value: '', notes: '', fullname: '',
});
const departments = ref([]);
const showMore = ref(false);

const getUserInfo = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/user/update/info`, {
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
    const response = await axios.post(`http://localhost:5000/user/update/info`, updateInfo.value, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    alert(response.data.message);
    router.push(`/${role}/dashboard`);
  } catch (error) {
    console.error(`Error: ${error}.`);
    alert(error?.response?.data?.message);
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

          <div class="mb-2">
            <p class="fw-semibold text-muted">User ID : {{ userDetails.id }}</p>
          </div>

          <div class="mb-3">
            <p class="fw-medium mb-1">Email: {{ userDetails.email }} </p>
          </div>

          <div class="mb-3">
            <p class="fw-medium mb-1">Full Name: {{ userDetails.fullname }}</p>
          </div>

          <div class="mb-3">
            <p class="fw-medium mb-1">Department: {{ userDetails.department }}</p>
          </div>

          <div class="mb-3">
            <p class="fw-medium mb-1">Experience: {{ extraDetails.experience }}</p>
          </div>

          <div class="mb-3">
              <p class="fw-medium mb-1">About: {{ showMore ? extraDetails.about : extraDetails.about.slice(0, 30) + '...'}}
              <span @click="showMore=!showMore" class="show-more">{{showMore ? 'less' : 'more'}}</span>
                </p>
          </div>

          <div class="mb-2">
            <p class="fw-medium mb-1">Request Information Update:</p>
            <select v-model="updateInfo.change" class="form-select" required>
              <option value="">Select attribute to change</option>
              <option> Full Name </option>
              <option> Department </option>
              <option> Experience </option>
              <option> About </option>
            </select>
            <input v-model="updateInfo.value" type="text" class="form-control mt-2" id="exampleInputData" placeholder="Enter new value" required>
          </div>

          <div class="mb-3">
            <p class="fw-medium mb-1">Enter reason for change: </p>
            <input v-model="updateInfo.notes" type="text" class="form-control mt-2" id="exampleInputData" placeholder="Notes" required>
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Send</button>
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
            <input v-model="updateInfo.fullname" type="text" class="form-control" id="exampleInputFullName" placeholder="New Full Name" required>
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Update</button>
            <button type="button" @click="router.back()" class="btn btn-secondary">
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