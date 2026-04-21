<template>
  <div class="card" style="padding: 18px">
    <div style="display: flex; align-items: baseline; justify-content: space-between; gap: 12px">
      <h2 style="margin: 0">我的订单</h2>
      <button v-if="auth.isAuthed" class="btn" :disabled="loading" @click="loadMe">刷新</button>
    </div>

    <p class="muted" style="margin: 12px 0 0; font-size: 14px">
      输入<strong>购票时使用的 11 位手机号</strong>即可查询该号码下所有订单及对应票务信息；无需身份证与姓名。
    </p>

    <div class="card" style="padding: 14px; margin-top: 14px">
      <div style="max-width: 320px">
        <div class="muted" style="margin-bottom: 6px">手机号</div>
        <input v-model.trim="phone" placeholder="11 位手机号" />
      </div>
      <div style="height: 12px" />
      <button class="btn primary" type="button" :disabled="querying" @click="queryByPhone">查询订单</button>
      <span class="muted" style="margin-left: 10px">{{ tip }}</span>
    </div>

    <div v-if="auth.isAuthed" class="muted" style="margin-top: 10px; font-size: 13px">
      你已登录支付身份：{{ auth.user?.phone }} · {{ auth.user?.full_name }} · 证件尾号 {{ auth.user?.id_card_last4 }}（可点「刷新」同步服务器订单）
    </div>

    <div style="height: 12px" />

    <div v-if="loading" class="muted">加载中...</div>
    <div v-else-if="error" class="muted">加载失败：{{ error }}</div>

    <div v-else-if="queried && orders.length === 0" class="muted">暂无订单记录。</div>

    <div v-else-if="orders.length > 0" style="display: grid; gap: 12px; margin-top: 8px">
      <div v-for="o in orders" :key="o.id" class="card" style="padding: 14px">
        <div style="display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap">
          <div style="font-weight: 800">订单 #{{ o.id }}</div>
          <div class="muted">{{ o.created_at }}</div>
        </div>

        <div style="height: 10px" />

        <div style="font-weight: 800; font-size: 16px">{{ o.ticket.title }}</div>
        <div class="muted" style="margin-top: 8px">场馆：{{ o.ticket.venue }}</div>
        <div class="muted" style="margin-top: 4px">演出时间：{{ o.ticket.start_time }}</div>
        <div class="muted" style="margin-top: 4px">
          单价：￥{{ (o.ticket.price_cents / 100).toFixed(2) }} · 购买数量：{{ o.quantity }} · 订单总价：￥{{
            (o.total_cents / 100).toFixed(2)
          }}
        </div>
        <div class="muted" style="margin-top: 4px">状态：{{ o.status }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { api, friendlyError } from '../lib/api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const phone = ref('')
const orders = ref([])
const loading = ref(false)
const querying = ref(false)
const error = ref('')
const tip = ref('')
const queried = ref(false)

async function loadMe() {
  if (!auth.isAuthed) return
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/api/orders/me')
    orders.value = data
    queried.value = true
    tip.value = data.length ? `共 ${data.length} 笔订单` : '暂无订单'
  } catch (e) {
    error.value = friendlyError(e)
  } finally {
    loading.value = false
  }
}

async function queryByPhone() {
  querying.value = true
  tip.value = ''
  error.value = ''
  try {
    const { data } = await api.post('/api/orders/lookup', { phone: phone.value })
    orders.value = data
    queried.value = true
    tip.value = data.length ? `共 ${data.length} 笔订单` : '该手机号下暂无订单'
  } catch (e) {
    error.value = friendlyError(e)
    orders.value = []
    queried.value = false
  } finally {
    querying.value = false
  }
}

onMounted(() => {
  if (auth.isAuthed) loadMe()
})

watch(
  () => auth.token,
  (t) => {
    if (!t) {
      orders.value = []
      queried.value = false
      tip.value = ''
      error.value = ''
      loading.value = false
    }
  }
)
</script>
