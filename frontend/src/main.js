import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'

axios.interceptors.response.use(
  response => response, 
  error => {
    if (error.response?.status === 401 && !error.config.url.includes('/login')) {
      localStorage.clear();
      router.push('/login');
    }
    if (error.response?.status === 403) {
      alert(error.response?.data?.message);
      router.back(); 
    }
    if (error.response?.status === 404) {
      alert(error.response?.data?.message);
      router.back();
    }
    return Promise.reject(error);
  }
)

const app = createApp(App)

app.use(router)

app.mount('#app')
