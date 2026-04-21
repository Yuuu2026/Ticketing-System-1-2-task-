<template>
  <div class="container">
    <header class="card" style="padding: 14px 16px; display: flex; align-items: center; gap: 12px">
      <div style="font-weight: 800; letter-spacing: 0.4px">购票网站</div>
      <nav style="display: flex; gap: 10px; margin-left: auto; align-items: center">
        <RouterLink class="btn" to="/">票务</RouterLink>
        <RouterLink class="btn" to="/orders">我的订单</RouterLink>
        <button v-if="isAuthed" type="button" class="btn" @click="logout">退出</button>
      </nav>
    </header>

    <main style="margin-top: 16px">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const { isAuthed } = storeToRefs(auth)
const router = useRouter()

function logout() {
  auth.logout()
  router.push('/orders').catch(() => {})
}
</script>

