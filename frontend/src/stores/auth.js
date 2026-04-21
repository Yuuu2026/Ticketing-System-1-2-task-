import { defineStore } from 'pinia'

const LS_TOKEN = 'ticketing_token'
const LS_USER = 'ticketing_user'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(LS_TOKEN) || '',
    user: JSON.parse(localStorage.getItem(LS_USER) || 'null')
  }),
  getters: {
    isAuthed: (s) => Boolean(s.token)
  },
  actions: {
    setAuth(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem(LS_TOKEN, token)
      localStorage.setItem(LS_USER, JSON.stringify(user))
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem(LS_TOKEN)
      localStorage.removeItem(LS_USER)
    }
  }
})

