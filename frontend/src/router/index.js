import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/components/Login.vue'
import Register from '@/components/Register.vue'
import AdminDashboard from '@/components/Admin/AdminDashboard.vue'
import AddDepartment from '@/components/Admin/AddDepartment.vue'
import EditDepartment from '@/components/Admin/EditDepartment.vue'
import AddDoctor from '@/components/Admin/AddDoctor.vue'
import EditUser from '@/components/Admin/EditUser.vue'
import UpdateRequests from '@/components/Admin/UpdateRequests.vue'
import Users from '@/components/Admin/Users.vue'
import Appointments from '@/components/Admin/Appointments.vue'
import Availability from '@/components/Admin/Availability.vue'
import DoctorDashboard from '@/components/Doctor/DoctorDashboard.vue'
import DoctorAvailability from '@/components/Doctor/DoctorAvailability.vue'
import Treatment from '@/components/Doctor/Treatment.vue'
import UpdateTreatment from '@/components/Doctor/UpdateTreatment.vue'
import DoctorProfile from '@/components/Doctor/DoctorProfile.vue'
import UpdateInfo from '@/components/Doctor/UpdateInfo.vue'
import PatientDashboard from '@/components/Patient/PatientDashboard.vue'
import AllDepartments from '@/components/Patient/AllDepartments.vue'
import ViewDepartment from '@/components/Patient/ViewDepartment.vue'
import DoctorBooking from '@/components/Patient/DoctorBooking.vue'
import PatientHistory from '@/components/Patient/PatientHistory.vue'
import Downloads from '@/components/Patient/Downloads.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: Login, },

    { path: '/', redirect: { path: '/login' }, },

    { path: '/register', name: 'register', component: Register, },

    { path: '/admin/dashboard', name: 'admin', component: AdminDashboard, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/add/department', name: 'add-department', component: AddDepartment, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/edit/department/:id', name: 'edit-department', component: EditDepartment, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/add/doctor', name: 'add-doctor', component: AddDoctor, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/edit/user/:id', name: 'edit-user', component: EditUser, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/requests', name: 'update-requests', component: UpdateRequests, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/users', name: 'users', component: Users, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/appointments', name: 'appointments', component: Appointments, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/availability/:id', name: 'availability', component: Availability, 
      meta: { requiresAuth: true, role: 'admin', } },

    { path: '/doctor/dashboard', name: 'doctor', component: DoctorDashboard, 
      meta: { requiresAuth: true, role: 'doctor' } },

    { path: '/doctor/availability', name: 'doctor-availability', component: DoctorAvailability, 
      meta: { requiresAuth: true, role: 'doctor' } },

    { path: '/doctor/treatment/:id', name: 'treatment', component: Treatment, 
      meta: { requiresAuth: true, role: 'doctor' } },

    { path: '/update/treatment/:id', name: 'update-treatment', component: UpdateTreatment, 
      meta: { requiresAuth: true, role: 'doctor' } },

    { path: '/doctor/profile/:id', name: 'doctor-profile', component: DoctorProfile, 
      meta: { requiresAuth: true } },

    { path: '/update/info', name: 'update-info', component: UpdateInfo, 
      meta: { requiresAuth: true } },

    { path: '/patient/dashboard', name: 'patient', component: PatientDashboard, 
      meta: { requiresAuth: true } },

    { path: '/departments', name: 'departments', component: AllDepartments, 
      meta: { requiresAuth: true } },

    { path: '/view/department/:id', name: 'view-department', component: ViewDepartment, 
      meta: { requiresAuth: true } },

    { path: '/book/doctor/:id', name: 'book-doctor', component: DoctorBooking, 
      meta: { requiresAuth: true } },

    { path: '/history/:patientId/:doctorId', name: 'patient-history', component: PatientHistory, 
      meta: { requiresAuth: true } },

    { path: '/downloads', name: 'downloads', component: Downloads, 
      meta: { requiresAuth: true } },
  ],
})

router.beforeEach((to, from) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  if (to.meta.requiresAuth && !token) {
    return { path: '/login' }
  }
  if (to.meta.role && to.meta.role !== role) {
    return { path: `/${role}/dashboard` }
  }
});

export default router
