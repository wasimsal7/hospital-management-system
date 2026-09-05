<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';

const route = useRoute();
const router = useRouter();

const availability = ref([]);
const booking = ref(null);

const groupedByDate = computed(() => {
  const map = {};
  for (const item of availability.value) {
    if (!map[item.date]) map[item.date] = {};
    map[item.date][item.slot] = item;
  }
  return map;
});

const isSelected = (item) => booking.value === item;

const selectSlot = (item) => {
  if (!item.available) {
    alert('This slot is currently unavailable or full!');
    return;
  }
  booking.value = item;
};

const getAvailability = async () => {
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(`http://localhost:5000/user/patient/book/doctor/${route.params.id}`, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    availability.value = response.data.availabilityData;
  } catch (error) {
    console.error(error);
  }
};

const confirmBooking = async () => {
  if (!booking.value) {
    alert("You haven't selected a slot!");
    return;
  }
  try {
    const token = localStorage.getItem('token');
    const payload = {
      date: booking.value.date,
      slot: booking.value.slot,
      time: booking.value.time,
    };
    const response = await axios.post(`http://localhost:5000/user/patient/book/doctor/${route.params.id}`, payload, {
      headers: { 'Authorization': `Bearer ${token}` },
    });
    alert(response.data.message);
    router.push('/patient/dashboard');
  } catch (error) {
    console.error(error);
    alert(error?.response?.data?.message || 'Error booking appointment');
  }
};

onMounted(getAvailability);
</script>

<template>
  <div class="container-lg my-4">
    <h3>Book Doctor</h3>
    <br>
    <table class="table table-bordered table-hover align-middle">
      <thead>
        <tr>
          <th>Date</th>
          <th>07 to 11 AM</th>
          <th>Seats Left</th>
          <th>04 to 08 PM</th>
          <th>Seats Left</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(slots, date) in groupedByDate" :key="date">
          <th>{{ new Date(date).toDateString() }}</th>

          <td>
            <button @click="selectSlot(slots.slot1)" :disabled="!slots.slot1.available"
              :class="isSelected(slots.slot1) ? 'btn btn-info' : (slots.slot1.available ? 'btn btn-outline-success' : 'btn btn-outline-danger')">
              {{ isSelected(slots.slot1) ? 'Selected' : (slots.slot1.available ? 'Select' : 'Unavailable') }}
            </button>
          </td>
          <td>
            <span :class="slots.slot1.seats_left > 0 ? 'text-success fw-bold' : 'text-danger fw-bold'">
              {{ slots.slot1.seats_left }}
            </span>
          </td>

          <td>
            <button @click="selectSlot(slots.slot2)" :disabled="!slots.slot2.available"
              :class="isSelected(slots.slot2) ? 'btn btn-info' : (slots.slot2.available ? 'btn btn-outline-success' : 'btn btn-outline-danger')">
              {{ isSelected(slots.slot2) ? 'Selected' : (slots.slot2.available ? 'Select' : 'Unavailable') }}
            </button>
          </td>
          <td>
            <span :class="slots.slot2.seats_left > 0 ? 'text-success fw-bold' : 'text-danger fw-bold'">
              {{ slots.slot2.seats_left }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>

    <button @click="confirmBooking" class="btn btn-primary mt-3">Confirm Booking</button>
    <button @click="router.push('/patient/dashboard')" class="btn btn-secondary ms-3 mt-3">Cancel</button>
  </div>
</template>

<style scoped>
</style>