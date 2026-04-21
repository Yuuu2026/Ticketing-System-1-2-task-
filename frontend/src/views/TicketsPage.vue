<template>
  <div class="card" style="padding: 18px">
    <div style="display: flex; align-items: baseline; justify-content: space-between; gap: 12px">
      <h2 style="margin: 0">票务列表</h2>
      <div class="muted" style="font-size: 13px">共 {{ tickets.length }} 场 · 支付时填写手机号、身份证、姓名</div>
    </div>

    <div style="height: 12px" />

    <div v-if="loading" class="muted">加载中...</div>
    <div v-else-if="error" class="muted">加载失败：{{ error }}</div>

    <div v-else style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px">
      <div v-for="t in tickets" :key="t.id" class="card" style="padding: 14px">
        <div style="font-weight: 800">{{ t.title }}</div>
        <div class="muted" style="margin-top: 6px">{{ t.venue }}</div>
        <div class="muted" style="margin-top: 6px">{{ t.start_time }}</div>
        <div style="margin-top: 10px; display: flex; align-items: center; justify-content: space-between; gap: 10px">
          <div>
            <div style="font-weight: 800">￥{{ (t.price_cents / 100).toFixed(2) }}</div>
            <div class="muted" style="font-size: 13px">余票：{{ t.stock }}</div>
          </div>
          <div style="display: flex; align-items: center; gap: 8px">
            <input v-model.number="qty[t.id]" type="number" min="1" style="width: 90px" />
            <button class="btn success" :disabled="t.stock <= 0 || paying" @click="openPay(t)">购票</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="pay.open" class="modal-mask" @click.self="closePay()">
    <div class="card modal">
      <div style="display: flex; justify-content: space-between; gap: 10px; align-items: center">
        <div style="font-weight: 800">支付 / 实名</div>
        <button class="btn" type="button" @click="closePay()">关闭</button>
      </div>

      <div style="height: 12px" />

      <div class="card" style="padding: 14px">
        <div style="font-weight: 800">{{ pay.ticket?.title }}</div>
        <div class="muted" style="margin-top: 6px">{{ pay.ticket?.venue }} · {{ pay.ticket?.start_time }}</div>
        <div style="height: 10px" />
        <div class="row" style="align-items: center; display: flex; flex-wrap: wrap; gap: 12px">
          <div style="min-width: 240px">
            <div class="muted" style="margin-bottom: 6px">购买数量</div>
            <input v-model.number="pay.quantity" type="number" min="1" />
          </div>
          <div style="flex: 1">
            <div class="muted">应付金额</div>
            <div style="font-weight: 900; font-size: 22px; margin-top: 6px">
              ￥{{ (((pay.ticket?.price_cents || 0) * (pay.quantity || 1)) / 100).toFixed(2) }}
            </div>
          </div>
        </div>
      </div>

      <div style="height: 12px" />
      <div v-if="auth.isAuthed" class="muted" style="font-size: 13px">
        当前身份：{{ auth.user?.phone }} · {{ auth.user?.full_name }} · 证件尾号 {{ auth.user?.id_card_last4 }}
      </div>

      <div v-if="!auth.isAuthed" class="card" style="padding: 14px; margin-top: 12px">
        <div style="font-weight: 800; margin-bottom: 8px">购票人信息</div>
        <div style="display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr))">
          <div>
            <div class="muted" style="margin-bottom: 6px">手机号</div>
            <input v-model.trim="pay.phone" placeholder="11 位手机号" />
          </div>
          <div>
            <div class="muted" style="margin-bottom: 6px">身份证号</div>
            <input v-model.trim="pay.id_card" placeholder="18 位或 15 位" />
          </div>
          <div style="grid-column: 1 / -1">
            <div class="muted" style="margin-bottom: 6px">姓名</div>
            <input v-model.trim="pay.full_name" placeholder="与证件一致" />
          </div>
        </div>
      </div>

      <div style="height: 12px" />

      <div style="display: flex; flex-wrap: wrap; gap: 12px; align-items: center">
        <button class="btn success" type="button" :disabled="paying" @click="confirmPay">确认支付</button>
        <div class="muted">{{ pay.tip }}</div>
      </div>
      <div class="muted" style="margin-top: 10px; font-size: 12px">
        未登录时将先核验手机号、身份证与姓名（新用户自动建档），再扣款出票。
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { api, friendlyError } from '../lib/api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()

const tickets = ref([])
const loading = ref(true)
const error = ref('')
const paying = ref(false)
const qty = reactive({})

const pay = reactive({
  open: false,
  ticket: null,
  quantity: 1,
  phone: '',
  id_card: '',
  full_name: '',
  tip: ''
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const { data } = await api.get('/api/tickets')
    tickets.value = data
    for (const t of data) {
      if (qty[t.id] == null) qty[t.id] = 1
    }
  } catch (e) {
    error.value = friendlyError(e)
  } finally {
    loading.value = false
  }
}

function openPay(t) {
  pay.open = true
  pay.ticket = t
  pay.quantity = Math.max(1, Number(qty[t.id] || 1))
  pay.tip = ''
  pay.phone = ''
  pay.id_card = ''
  pay.full_name = ''
}

function closePay() {
  pay.open = false
  pay.ticket = null
  pay.tip = ''
}

async function ensureAuthForPay() {
  if (auth.isAuthed) return true
  const phone = pay.phone.trim()
  const id_card = pay.id_card.trim()
  const full_name = pay.full_name.trim()
  if (!phone || !id_card || !full_name) {
    pay.tip = '请填写手机号、身份证号与姓名'
    return false
  }
  try {
    const { data } = await api.post('/api/auth/session', { phone, id_card, full_name })
    auth.setAuth(data.access_token, data.user)
    return true
  } catch (e) {
    pay.tip = friendlyError(e)
    return false
  }
}

async function confirmPay() {
  const t = pay.ticket
  if (!t) return
  paying.value = true
  pay.tip = ''
  try {
    const ok = await ensureAuthForPay()
    if (!ok) return
    const quantity = Math.max(1, Number(pay.quantity || 1))
    const { data } = await api.post('/api/orders', { ticket_id: t.id, quantity })
    closePay()
    pay.tip = ''
    await load()
    alert(`支付成功：订单 #${data.id}，数量 ${data.quantity}`)
  } catch (e) {
    pay.tip = friendlyError(e)
  } finally {
    paying.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  z-index: 50;
}
.modal {
  width: min(720px, 100%);
  padding: 16px;
}
</style>
