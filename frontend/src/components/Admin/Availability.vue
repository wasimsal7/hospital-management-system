<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';

const router = useRouter();
const route = useRoute();
const available = ref([]); 

const groupedByDate = computed(() => {
  const map = {};
  for (const item of available.value) {
    if (!map[item.date]) map[item.date] = {};
    map[item.date][item.slot] = item;
  }
  return map;
});

const getAvailability = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/admin/doctor/availability/${route.params.id}`, {
      headers: { 
        'Authorization': `Bearer ${token}` 
      },
    });
    available.value = response.data.availabilityData;
  } catch (error) {
    console.error(error);
    alert(error?.response?.data?.message || 'Error fetching availability');
  }
};

const setAvailability = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.post(`http://localhost:5000/admin/doctor/availability/${route.params.id}`, available.value, {
      headers: { 
        'Authorization': `Bearer ${token}` 
      },
    });
    alert(response.data.message);
  } catch (error) {
    console.error(error);
    alert(error?.response?.data?.message || 'Error saving availability');
  }
};

onMounted(getAvailability);
</script>

<template>
  <div class="container my-4">
    <h3>Availability</h3>
    <br>
    <table class="table table-bordered table-hover align-middle">
      <thead>
        <tr>
          <th>Date</th>
          <th>07 to 11 AM</th>
          <th>Limit</th>
          <th>04 to 08 PM</th>
          <th>Limit</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(slots, date) in groupedByDate" :key="date">
          <th>{{ new Date(date).toDateString() }}</th>

          <td>
            <button @click="slots.slot1.is_available = !slots.slot1.is_available"
              :class="slots.slot1.is_available ? 'btn btn-success btn' : 'btn btn-danger btn'">
              {{ slots.slot1.is_available ? 'Available' : 'Unavailable' }}
            </button>
          </td>
          <td>
            <input v-model.number="slots.slot1.limit" type="number" class="form-control form-control-sm"
              style="width: 70px;" min="1" max="10" :disabled="!slots.slot1.is_available">
          </td>

          <td>
            <button @click="slots.slot2.is_available = !slots.slot2.is_available"
              :class="slots.slot2.is_available ? 'btn btn-success btn' : 'btn btn-danger btn'">
              {{ slots.slot2.is_available ? 'Available' : 'Unavailable' }}
            </button>
          </td>
          <td>
            <input v-model.number="slots.slot2.limit" type="number" class="form-control form-control-sm"
              style="width: 70px;" min="1" max="10" :disabled="!slots.slot2.is_available">
          </td>
        </tr>
      </tbody>
    </table>
    <button @click="setAvailability" class="btn btn-primary">Save Availability</button>
    <button @click="router.back()" class="btn btn-secondary ms-3">Cancel</button>
  </div>
</template>
<style scoped>

</style>