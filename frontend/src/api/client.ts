import axios from 'axios'
import { getToken, clearSession } from '@/auth/session'
import router from '@/router'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
    'X-Requested-With': 'XMLHttpRequest',
  },
})

apiClient.interceptors.request.use(config => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let isRedirecting = false

apiClient.interceptors.response.use(
  res => res,
  async (err) => {
    if (err.response?.status === 401 && !isRedirecting) {
      isRedirecting = true
      clearSession()
      await router.push({ path: '/login', query: { reason: 'session_expired' } })
      isRedirecting = false
    }
    return Promise.reject(err)
  },
)
