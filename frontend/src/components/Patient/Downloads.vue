<script setup>

import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const downloads = ref([]);

const getDownloads = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get('http://localhost:5000/user/downloads', {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    downloads.value = response.data.downloads;
  } catch(error) {
    console.error(`Error: ${error}.`)
  }
};

const downloadFile = async (id) => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/user/download/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }, 
      responseType: 'blob',
    })
    const url = window.URL.createObjectURL(response.data);
    const link = document.createElement('a');
    link.href = url
    link.download = `patient_download_${id}.csv`;
    link.click()
  } catch (error) {
    console.error(`Error ${error}.`);
  }
};

const deleteFile = async (id) => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.delete(`http://localhost:5000/user/download/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    getDownloads();
  } catch (error) {
    console.error(`Error: ${error}.`);
  }
}

onMounted(getDownloads);

</script>

<template>

  <div class="container my-4">
    <h1>Downloads</h1>
    <br>
    <p v-if="downloads.length === 0" class="text-muted">No downloads found.</p>
    <table v-else class="table table-bordered table-hover">
      <thead>
        <tr>
          <th scope="col">Filename</th>
          <th scope="col">Created At</th>
          <th scope="col">Download Status</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="download in downloads" :key="download.id">
          <td>{{ download.filename }}</td>
          <td>{{ download.createdAt }}</td>
          <td>{{ download.downloadStatus }}</td>
          <td>
            <div class="d-flex gap-3">
              <button @click="downloadFile(download.id)" type="button" class="btn btn-primary">Download</button>
              <button @click="deleteFile(download.id)" type="button" class="btn btn-danger">Delete</button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>
    <button @click="router.back()" class="btn btn-secondary">Back</button>
  </div>

</template>

<style scoped>

</style>