import { ref, onMounted, onUnmounted } from 'vue'
import { msUntilExpiry } from '@/auth/session'
import { useAuthStore } from '@/stores/auth'

const WARN_BEFORE_MS = 5 * 60 * 1000

export function useSessionTimeout() {
  const showWarning  = ref(false)
  const minutesLeft  = ref(0)

  let warnTimer: ReturnType<typeof setTimeout>
  let logoutTimer: ReturnType<typeof setTimeout>
  let countdown: ReturnType<typeof setInterval>

  function clear() {
    clearTimeout(warnTimer); clearTimeout(logoutTimer); clearInterval(countdown)
  }

  function start() {
    clear()
    const ms = msUntilExpiry()
    if (ms <= 0) { useAuthStore().logout(); return }

    logoutTimer = setTimeout(() => { useAuthStore().logout() }, ms)

    if (ms > WARN_BEFORE_MS) {
      warnTimer = setTimeout(() => {
        showWarning.value = true
        minutesLeft.value = Math.ceil(WARN_BEFORE_MS / 60_000)
        countdown = setInterval(() => {
          minutesLeft.value = Math.ceil(msUntilExpiry() / 60_000)
          if (minutesLeft.value <= 0) clear()
        }, 10_000)
      }, ms - WARN_BEFORE_MS)
    } else {
      showWarning.value = true
    }
  }

  function dismiss() { showWarning.value = false; start() }

  onMounted(start)
  onUnmounted(clear)

  return { showWarning, minutesLeft, dismiss }
}
