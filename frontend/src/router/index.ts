import { createRouter, createWebHistory } from 'vue-router'
import { getSession } from '@/auth/session'
import { isFA, canAccess, hasPosition } from '@/auth/permissions'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/budget' },
    { path: '/login',  component: () => import('@/views/LoginView.vue') },
    { path: '/finance', component: () => import('@/views/finance/FinanceView.vue'), meta: { requiresAuth: true, page: 'finance' } },
    { path: '/budget',  component: () => import('@/views/finance/BudgetView.vue'),  meta: { requiresAuth: true, page: 'budget'  } },
    { path: '/io',      component: () => import('@/views/finance/IoView.vue'),       meta: { requiresAuth: true, page: 'io'      } },
    { path: '/admin',   component: () => import('@/views/admin/AdminView.vue'),      meta: { requiresAuth: true, requiresFAPosition: true } },
    { path: '/:pathMatch(.*)*', redirect: '/budget' },
  ],
})

router.beforeEach((to, _from, next) => {
  const session  = getSession()
  const auth     = session !== null
  const role     = session?.role ?? ''
  const position = session?.position ?? null
  const coord    = session?.coordinator ?? false

  if (to.meta.requiresAuth && !auth)                                   return next('/login')
  if (to.meta.requiresAuth && auth && !hasPosition(position) && !coord && !isFA(role)) return next('/login')
  if (to.meta.requiresFAPosition && (!isFA(role) || !hasPosition(position)))           return next('/budget')
  if (to.path === '/login' && auth)                                    return next(isFA(role) ? '/finance' : '/budget')

  const page = to.meta.page as string | undefined
  if (page && auth && !canAccess(role, page)) return next('/budget')

  next()
})

export default router
