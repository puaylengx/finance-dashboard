import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '@/router'
import { saveSession, getSession, clearSession, type AuthUser } from '@/auth/session'
import { isFA, isDivision, hasPosition } from '@/auth/permissions'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(getSession())

  const isLoggedIn            = computed(() => user.value !== null)
  const role                  = computed(() => user.value?.role ?? '')
  const position              = computed(() => user.value?.position ?? null)
  const isCoordinator         = computed(() => user.value?.coordinator ?? false)
  const isUserFA              = computed(() => isFA(role.value))
  const isUserDiv             = computed(() => isDivision(role.value))
  const hasPos                = computed(() => hasPosition(position.value))
  const canViewBudget         = computed(() => isLoggedIn.value)
  const canManageCoordinators = computed(() => isUserFA.value && hasPos.value)

  function setUser(token: string, tokenResponse: {
    role: string; position: string | null; coordinator: boolean
    name: string; expires_in: number
  }, username: string) {
    const authUser: AuthUser = {
      name: tokenResponse.name, username,
      role: tokenResponse.role, position: tokenResponse.position,
      coordinator: tokenResponse.coordinator, token,
      expiresAt: Date.now() + tokenResponse.expires_in * 1000,
    }
    user.value = authUser
    saveSession(authUser)
  }

  function logout() {
    user.value = null
    clearSession()
    router.push('/login')
  }

  return {
    user, isLoggedIn, role, position, isCoordinator,
    isUserFA, isUserDiv, hasPos, canViewBudget, canManageCoordinators,
    setUser, logout,
  }
})
