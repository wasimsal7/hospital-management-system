<script setup>

import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const requestsData = ref([]);
const reasonPrompt = ref(false);
const formData = ref({
  id: '', reason: '',
});
const copiedId = ref(null);

const copy = async (id, text) => {
  try {
    await navigator.clipboard.writeText(text);
    copiedId.value = id;
    setTimeout(() => {
      copiedId.value = null;
    }, 3000)
  } catch (error) {
    console.error(`Error: ${error}.`)
  }
}

const getRequests = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5000/admin/requests', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    requestsData.value = response.data.requestsData;
  } catch (error) {
    console.error(`Error: ${error}.`)
  }
}

const acceptRequest = (id) => {
  router.push(`/edit/user/${id}`);
};

const openReject = (id) => {
  formData.value.id = id;
  reasonPrompt.value = true;
}

const rejectRequest = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(`http://localhost:5000/admin/request/${formData.value.id}`, formData.value, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    reasonPrompt.value = false;
    formData.value = {reason: '', change: ''};
    alert(response.data.message);
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
};

const deleteRequest = async (id) => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.delete(`http://localhost:5000/admin/request/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    getRequests();
  } catch (error) {
    console.error(`Error: ${error}.`)
  }
};

onMounted(getRequests);
</script>

<template>

  <div v-if="!reasonPrompt" class="container my-4">
    <h3> Update Requests </h3>
    <p v-if="requestsData.length === 0" class="text-muted">
      No new requests.
    </p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Doctor ID</th>
          <th scope="col">Email</th>
          <th scope="col">Full Name</th>
          <th scope="col">Change</th>
          <th scope="col">New Value</th>
          <th scope="col">Notes</th>
          <th scope="col">Actions</th>
          <th scope="col">Clear</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="request in requestsData" :key="request.id">
          <th scope="row">{{ request.doctor_id }}</th>
          <td>{{ request.doctor_email }}</td>
          <td>{{ request.doctor_fullname }}</td>
          <td>{{ request.change }}</td>
          <td>
            <div class="d-flex gap-2">
              {{ request.value }} 
              <i :class="copiedId === request.id ? 'bi bi-clipboard-check' : 'bi bi-copy'" 
              @click="copy(request.id, request.value)" style="cursor: pointer;"></i>
            </div>
          </td>
          <td>{{ request.notes }}</td>
          <td>
            <div class="d-flex gap-3 mt-0">
              <button @click="acceptRequest(request.doctor_id)" class="btn btn-success">Accept</button>
              <button @click="openReject(request.id)" class="btn btn-danger">Reject</button>
            </div>
          </td>
          <td>
            <button @click="deleteRequest(request.id)" class="btn btn-secondary">
              <i class="bi bi-trash"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <div v-else class="form-wrapper d-flex justify-content-center align-items-center">
    <div class="form-card card shadow-lg border-2">
      <div class="card-body p-5">
        <h1 class="fw-bold text-center mb-5">Reject Request</h1>
    
        <form @submit.prevent="rejectRequest">

          <div class="mb-4">
            <p>Enter reason for rejection: </p>
            <input v-model="formData.reason" type="text" class="form-control" placeholder="Reason" required>
          </div>

          <div class="d-flex gap-3 mt-4">
            <button type="submit" class="btn btn-primary">Send</button>
            <button type="button" @click="reasonPrompt=false" class="btn btn-secondary">
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
  max-width: 450px;
  border-radius: 15px;
}

</style>