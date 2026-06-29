import { createRouter, createWebHistory } from 'vue-router'
import { getSession } from '@/auth/session'
import { isFA, canAccess, hasPosition } from '@/auth/permissions'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/io' },
    { path: '/login',  component: () => import('@/views/LoginView.vue') },
    { path: '/budget', component: () => import('@/views/budget/BudgetView.vue'), meta: { requiresAuth: true, page: 'budget' } },
    { path: '/io',     component: () => import('@/views/budget/IoView.vue'),     meta: { requiresAuth: true, page: 'io'     } },
    { path: '/admin',   component: () => import('@/views/admin/AdminView.vue'),      meta: { requiresAuth: true, requiresFAPosition: true } },
    { path: '/:pathMatch(.*)*', redirect: '/io' },
  ],
})

router.beforeEach((to, _from, next) => {
  const session     = getSession()
  const auth        = session !== null
  const role        = session?.role ?? ''
  const position    = session?.position ?? null
  const coordinator = session?.coordinator ?? false

  if (to.meta.requiresAuth && !auth)                                              return next('/login')
  if (to.meta.requiresAuth && auth && role === 'user' && !coordinator) return next('/login')
  if (to.meta.requiresFAPosition && (!isFA(role) || !hasPosition(position)))           return next('/io')
  if (to.path === '/login' && auth)                                    return next('/budget')

  const page = to.meta.page as string | undefined
  if (page && auth && !canAccess(role, page)) return next('/io')

  next()
})

export default router
