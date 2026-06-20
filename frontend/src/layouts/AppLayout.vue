<template>
  <div class="min-h-screen bg-bg flex">
    <!-- Sidebar -->
    <aside class="w-56 shrink-0 flex flex-col border-r border-border bg-surface">
      <!-- Logo -->
      <div class="px-5 py-4 border-b border-border">
        <div class="text-sm font-semibold text-accent">Finance Dashboard</div>
        <div class="text-xs text-muted mt-0.5 truncate">{{ auth.user?.name }}</div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-4 px-3 flex flex-col gap-1">
        <RouterLink v-if="auth.canViewFinance" to="/finance" class="nav-link">Finance</RouterLink>
        <RouterLink to="/budget" class="nav-link">Budget</RouterLink>
        <RouterLink to="/io"     class="nav-link">IO Dashboard</RouterLink>
        <RouterLink v-if="auth.canManageCoordinators" to="/admin" class="nav-link">Admin</RouterLink>
      </nav>

      <!-- Bottom actions -->
      <div class="p-3 border-t border-border flex flex-col gap-1">
        <!-- Theme toggle -->
        <button
          @click="themeCtrl.toggle()"
          class="w-full flex items-center gap-2 text-xs text-muted hover:text-fg transition-colors px-3 py-2 rounded-lg hover:bg-surface2"
        >
          <svg v-if="themeCtrl.theme.value === 'dark'" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
          </svg>
          <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
          </svg>
          {{ themeCtrl.theme.value === 'dark' ? 'Light mode' : 'Dark mode' }}
        </button>

        <!-- Logout -->
        <button
          @click="auth.logout()"
          class="w-full text-left text-xs text-muted hover:text-danger transition-colors px-3 py-2 rounded-lg hover:bg-surface2"
        >
          ออกจากระบบ
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top bar -->
      <header class="h-14 border-b border-border flex items-center px-6 gap-4 bg-surface">
        <h1 class="text-sm font-semibold text-fg flex-1">{{ pageTitle }}</h1>
        <div class="flex items-center gap-3">
          <span class="text-xs px-2 py-1 rounded-full border" :class="roleBadgeClass">{{ auth.role }}</span>
          <span v-if="auth.position" class="text-xs text-muted">{{ auth.position }}</span>
        </div>
      </header>

      <!-- Page slot -->
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>

    <!-- Session timeout warning -->
    <Transition name="slide-up">
      <div v-if="timeout.showWarning.value"
        class="fixed bottom-4 right-4 z-50 rounded-xl border border-warning bg-surface p-4 w-72 shadow-xl">
        <div class="text-sm text-warning font-medium mb-1">Session ใกล้หมดเวลา</div>
        <div class="text-xs text-muted">เหลือเวลา {{ timeout.minutesLeft.value }} นาที</div>
        <button @click="timeout.dismiss()" class="mt-3 text-xs text-accent hover:underline">รับทราบ</button>
      </div>
    </Transition>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSessionTimeout } from '@/composables/useSessionTimeout'
import { useTheme } from '@/composables/useTheme'

const auth      = useAuthStore()
const route     = useRoute()
const timeout   = useSessionTimeout()
const themeCtrl = useTheme()

const PAGE_TITLES: Record<string, string> = {
  '/finance': 'Finance', '/budget': 'Budget', '/io': 'IO Dashboard', '/admin': 'Admin',
}
const pageTitle = computed(() => PAGE_TITLES[route.path] ?? 'Finance Dashboard')

const roleBadgeClass = computed(() => {
  const r = auth.role.toLowerCase()
  if (r === 'fa') return 'border-accent text-accent'
  if (['bba','hld','sci','ss','thm','faa','mba','mm'].includes(r)) return 'border-success text-success'
  return 'border-muted text-muted'
})
</script>
<style scoped>
@reference "../style.css";
.nav-link {
  @apply block px-3 py-2 text-sm text-muted rounded-lg hover:bg-surface2 hover:text-fg transition-colors;
}
.nav-link.router-link-active {
  @apply bg-surface2 text-accent;
}
</style>
