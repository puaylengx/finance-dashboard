<template>
  <div class="min-h-screen bg-bg flex font-sans">

    <!-- ── Sidebar ── -->
    <aside class="w-56 bg-surface border-r border-border flex flex-col shrink-0 fixed inset-y-0 left-0 z-30 shadow-sm">

      <!-- Logo -->
      <div class="px-5 pt-5 pb-4 flex items-center gap-2.5">
        <div class="w-9 h-9 bg-linear-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center shrink-0 shadow-md shadow-indigo-100/50">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round"
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <div>
          <p class="text-sm font-bold text-fg leading-none">Finance</p>
          <p class="text-[11px] text-muted mt-0.5">Dashboard</p>
        </div>
      </div>

      <!-- Nav -->
      <nav class="px-3 py-2 flex-1 flex flex-col gap-0.5 overflow-y-auto">
        <p class="text-[10px] font-semibold text-muted uppercase tracking-widest px-2 mb-2">Menu</p>

        <RouterLink v-if="auth.canViewFinance" to="/finance" :class="navClass('/finance')">
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/>
          </svg>
          Finance
        </RouterLink>

        <RouterLink to="/budget" :class="navClass('/budget')">
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"/>
          </svg>
          Budget
        </RouterLink>

        <RouterLink to="/io" :class="navClass('/io')">
          <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
          </svg>
          IO Breakdown
        </RouterLink>

        <template v-if="auth.canManageCoordinators">
          <p class="text-[10px] font-semibold text-muted uppercase tracking-widest px-2 mt-4 mb-2">Administration</p>
          <RouterLink to="/admin" :class="navClass('/admin')">
            <svg class="w-4 h-4 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
            </svg>
            Admin
          </RouterLink>
        </template>
      </nav>

      <!-- Bottom: user + theme toggle + logout -->
      <div class="px-4 py-4 border-t border-border space-y-2">
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

        <!-- User -->
        <div class="flex items-center gap-2.5 px-1">
          <div class="w-8 h-8 rounded-full bg-linear-to-br from-indigo-400 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shrink-0 uppercase shadow-sm">
            {{ auth.user?.name?.charAt(0) ?? 'U' }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-xs font-semibold text-fg truncate">{{ auth.user?.name ?? 'Guest' }}</p>
            <p class="text-[10px] text-muted truncate uppercase">{{ auth.role }}</p>
          </div>
          <button @click="auth.logout()" title="Logout"
            class="w-7 h-7 flex items-center justify-center text-muted hover:text-danger hover:bg-danger/10 rounded-lg transition-colors">
            <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
            </svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- ── Main ── -->
    <div class="flex-1 flex flex-col ml-56 min-h-screen">

      <!-- Top bar -->
      <header class="bg-surface border-b border-border px-6 py-3.5 flex justify-between items-center sticky top-0 z-20">
        <div>
          <h1 class="text-base font-bold text-fg">{{ resolvedTitle }}</h1>
          <p class="text-[11px] text-muted mt-0.5">{{ fmtDate() }}</p>
        </div>
        <div class="flex items-center gap-2.5">
          <!-- Export buttons -->
          <template v-if="showExport">
            <button @click="emit('export-excel')"
              class="flex items-center gap-1.5 bg-linear-to-r from-indigo-600 to-indigo-500 text-white text-xs font-semibold px-3 py-2 rounded-lg hover:from-indigo-700 hover:to-indigo-600 transition-all shadow-md shadow-indigo-100/50">
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
              </svg>
              Excel
            </button>
            <button @click="emit('export-csv')"
              class="text-xs font-medium text-muted border border-border px-3 py-2 rounded-lg hover:bg-surface2 hover:text-fg transition">
              CSV
            </button>
            <button @click="emit('print')"
              class="text-xs font-medium text-muted border border-border px-3 py-2 rounded-lg hover:bg-surface2 hover:text-fg transition no-print">
              Print
            </button>
          </template>

          <!-- Role badge -->
          <span class="text-xs px-2 py-1 rounded-full border" :class="roleBadgeClass">{{ auth.role }}</span>
        </div>
      </header>

      <!-- Page slot -->
      <main class="flex-1 p-6 space-y-4">
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

const props = withDefaults(defineProps<{ title?: string; showExport?: boolean }>(), {
  showExport: false,
})
const emit = defineEmits<{
  'export-excel': []
  'export-csv':   []
  'print':        []
}>()

const auth      = useAuthStore()
const route     = useRoute()
const timeout   = useSessionTimeout()
const themeCtrl = useTheme()

const PAGE_TITLES: Record<string, string> = {
  '/finance': 'Finance', '/budget': 'Budget', '/io': 'IO Dashboard', '/admin': 'Admin',
}
const resolvedTitle = computed(() => props.title ?? PAGE_TITLES[route.path] ?? 'Finance Dashboard')

function fmtDate(): string {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
  })
}

function navClass(path: string): string {
  return route.path === path
    ? 'flex items-center gap-2.5 px-3 py-2.5 rounded-xl bg-linear-to-r from-indigo-600 to-indigo-500 text-white text-sm font-semibold shadow-md shadow-indigo-100/50 transition-all duration-200'
    : 'flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-muted hover:text-fg hover:bg-surface2 text-sm transition-all duration-200'
}

const roleBadgeClass = computed(() => {
  const r = auth.role.toLowerCase()
  if (r === 'fa') return 'border-accent text-accent'
  if (['bba','hld','sci','ss','thm','faa','mba','mm'].includes(r)) return 'border-success text-success'
  return 'border-muted text-muted'
})
</script>
