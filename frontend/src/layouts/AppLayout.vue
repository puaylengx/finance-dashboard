<template>
  <div class="min-h-screen bg-[#0f1117] flex">
    <!-- Sidebar -->
    <aside class="w-56 shrink-0 flex flex-col border-r border-[#2e3250] bg-[#1a1d27]">
      <!-- Logo -->
      <div class="px-5 py-4 border-b border-[#2e3250]">
        <div class="text-sm font-semibold text-[#6c8efb]">Finance Dashboard</div>
        <div class="text-xs text-[#8892b0] mt-0.5 truncate">{{ auth.user?.name }}</div>
      </div>

      <!-- Nav -->
      <nav class="flex-1 py-4 px-3 flex flex-col gap-1">
        <RouterLink v-if="auth.canViewFinance" to="/finance" class="nav-link">Finance</RouterLink>
        <RouterLink to="/budget" class="nav-link">Budget</RouterLink>
        <RouterLink to="/io"     class="nav-link">IO Dashboard</RouterLink>
        <RouterLink v-if="auth.canManageCoordinators" to="/admin" class="nav-link">Admin</RouterLink>
      </nav>

      <!-- Logout -->
      <div class="p-3 border-t border-[#2e3250]">
        <button @click="auth.logout()" class="w-full text-left text-xs text-[#8892b0] hover:text-[#f87171] transition-colors px-3 py-2 rounded-lg hover:bg-[#22263a]">
          ออกจากระบบ
        </button>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Top bar -->
      <header class="h-14 border-b border-[#2e3250] flex items-center px-6 gap-4 bg-[#1a1d27]">
        <h1 class="text-sm font-semibold text-[#e2e8f0] flex-1">{{ pageTitle }}</h1>
        <div class="flex items-center gap-3">
          <span class="text-xs px-2 py-1 rounded-full border"
            :class="roleBadgeClass">{{ auth.role }}</span>
          <span v-if="auth.position" class="text-xs text-[#8892b0]">{{ auth.position }}</span>
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
        class="fixed bottom-4 right-4 z-50 rounded-xl border border-[#fbbf24] bg-[#1a1d27] p-4 w-72 shadow-xl">
        <div class="text-sm text-[#fbbf24] font-medium mb-1">Session ใกล้หมดเวลา</div>
        <div class="text-xs text-[#8892b0]">เหลือเวลา {{ timeout.minutesLeft.value }} นาที</div>
        <button @click="timeout.dismiss()" class="mt-3 text-xs text-[#6c8efb] hover:underline">รับทราบ</button>
      </div>
    </Transition>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useSessionTimeout } from '@/composables/useSessionTimeout'

const auth    = useAuthStore()
const route   = useRoute()
const timeout = useSessionTimeout()

const PAGE_TITLES: Record<string, string> = {
  '/finance': 'Finance', '/budget': 'Budget', '/io': 'IO Dashboard', '/admin': 'Admin',
}
const pageTitle = computed(() => PAGE_TITLES[route.path] ?? 'Finance Dashboard')

const roleBadgeClass = computed(() => {
  const r = auth.role.toLowerCase()
  if (r === 'fa')  return 'border-[#6c8efb] text-[#6c8efb]'
  if (['bba','hld','sci','ss','thm','faa','mba','mm'].includes(r)) return 'border-[#34d399] text-[#34d399]'
  return 'border-[#8892b0] text-[#8892b0]'
})
</script>
<style scoped>
@reference "../style.css";
.nav-link {
  @apply block px-3 py-2 text-sm text-[#8892b0] rounded-lg hover:bg-[#22263a] hover:text-[#e2e8f0] transition-colors;
}
.nav-link.router-link-active {
  @apply bg-[#22263a] text-[#6c8efb];
}
</style>
