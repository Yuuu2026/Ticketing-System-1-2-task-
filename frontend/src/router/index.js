import { createRouter, createWebHistory } from 'vue-router'
import TicketsPage from '../views/TicketsPage.vue'
import OrdersPage from '../views/OrdersPage.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: TicketsPage },
    { path: '/login', redirect: '/orders' },
    { path: '/orders', component: OrdersPage }
  ]
})
