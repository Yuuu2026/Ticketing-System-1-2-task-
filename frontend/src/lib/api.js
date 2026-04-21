import axios from 'axios'
import { useAuthStore } from '../stores/auth'

export const api = axios.create({
  baseURL: 'http://127.0.0.1:5000'
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${auth.token}`
  }
  return config
})

export function friendlyError(err) {
  const msg =
    err?.response?.data?.message ||
    err?.message ||
    '请求失败'
  return String(msg)
}

