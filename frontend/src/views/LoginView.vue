<template>
  <div class="min-h-screen bg-bg flex items-center justify-center px-4 py-10">

    <!-- Theme toggle (top-right) -->
    <button
      @click="themeCtrl.toggle()"
      class="fixed top-4 right-4 w-9 h-9 rounded-xl border border-border bg-surface flex items-center justify-center text-muted hover:text-fg hover:border-accent transition-colors z-10"
      :title="themeCtrl.theme.value === 'dark' ? 'Switch to Light' : 'Switch to Dark'"
    >
      <svg v-if="themeCtrl.theme.value === 'dark'" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
        <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
      </svg>
      <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
    </button>

    <div class="w-full max-w-md animate-fade-in">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-accent/15 border border-accent/30 mb-4">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
            <line x1="12" y1="12" x2="12" y2="16"/><line x1="10" y1="14" x2="14" y2="14"/>
          </svg>
        </div>
        <h1 class="text-xl font-bold text-fg">Finance Dashboard</h1>
        <p class="text-sm text-muted mt-1">เลือกหน่วยงานและตำแหน่งเพื่อเข้าสู่ระบบ</p>
      </div>

      <div class="rounded-2xl border border-border bg-surface p-6 flex flex-col gap-6">

        <!-- Step 1: Role -->
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="w-5 h-5 rounded-full bg-accent/20 border border-accent/40 text-accent text-xs flex items-center justify-center font-semibold">1</span>
            <span class="text-sm font-medium text-fg">เลือกหน่วยงาน</span>
          </div>

          <!-- FA special card -->
          <div class="mb-3">
            <button type="button" @click="selectedRole = 'fa'" class="role-card w-full" :class="selectedRole === 'fa' ? 'role-card--active' : ''">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                  :class="selectedRole === 'fa' ? 'bg-accent/25' : 'bg-surface2'">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    class="transition-colors" :class="selectedRole === 'fa' ? 'text-accent' : 'text-muted'">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <div class="text-left">
                  <div class="text-sm font-semibold" :class="selectedRole === 'fa' ? 'text-accent' : 'text-fg'">FA</div>
                  <div class="text-xs text-muted">Finance &amp; Accounting</div>
                </div>
              </div>
              <div v-if="selectedRole === 'fa'" class="w-4 h-4 rounded-full bg-accent flex items-center justify-center shrink-0">
                <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            </button>
          </div>

          <!-- Division grid -->
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="div in DIVISIONS" :key="div.value"
              type="button" @click="selectedRole = div.value"
              class="div-card" :class="selectedRole === div.value ? 'div-card--active' : ''"
            >
              <div class="text-sm font-bold leading-tight" :class="selectedRole === div.value ? 'text-accent' : 'text-fg'">{{ div.label }}</div>
              <div class="text-[10px] leading-tight mt-0.5" :class="selectedRole === div.value ? 'text-accent/70' : 'text-muted'">{{ div.sub }}</div>
            </button>
          </div>
        </div>

        <!-- Step 2: Position -->
        <Transition name="slide-up">
          <div v-if="selectedRole">
            <div class="flex items-center gap-2 mb-3">
              <span class="w-5 h-5 rounded-full bg-accent/20 border border-accent/40 text-accent text-xs flex items-center justify-center font-semibold">2</span>
              <span class="text-sm font-medium text-fg">ตำแหน่ง</span>
              <span class="text-xs text-muted">(ถ้ามี)</span>
            </div>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="pos in POSITIONS" :key="pos.value"
                type="button"
                @click="selectedPosition = selectedPosition === pos.value ? null : pos.value"
                class="pos-pill" :class="selectedPosition === pos.value ? 'pos-pill--active' : ''"
              >{{ pos.label }}</button>
            </div>
          </div>
        </Transition>

        <!-- Step 3: Name -->
        <Transition name="slide-up">
          <div v-if="selectedRole">
            <div class="flex items-center gap-2 mb-3">
              <span class="w-5 h-5 rounded-full bg-accent/20 border border-accent/40 text-accent text-xs flex items-center justify-center font-semibold">3</span>
              <span class="text-sm font-medium text-fg">ชื่อ-นามสกุล</span>
            </div>
            <input
              v-model="name" type="text" placeholder="กรอกชื่อ-นามสกุล"
              class="w-full bg-surface2 border border-border rounded-xl px-4 py-2.5 text-sm text-fg outline-none placeholder:text-placeholder focus:border-accent transition-colors"
              autocomplete="off" @keydown.enter="handleLogin"
            />
          </div>
        </Transition>

        <!-- Error -->
        <div v-if="error" class="text-xs text-danger rounded-lg border border-danger/30 bg-danger/10 px-3 py-2">
          {{ error }}
        </div>

        <!-- Summary + Submit -->
        <div v-if="selectedRole" class="flex items-center gap-3">
          <div class="flex-1 text-xs text-muted bg-surface2 rounded-lg px-3 py-2 font-mono">
            {{ jobTitlePreview }}
          </div>
          <button
            type="button" :disabled="loading || !name.trim()" @click="handleLogin"
            class="px-5 py-2.5 rounded-xl bg-accent text-white text-sm font-medium hover:bg-accent-h transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
          >
            {{ loading ? '...' : 'เข้าสู่ระบบ' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { draftLogin } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { isFA } from '@/auth/permissions'
import { useTheme } from '@/composables/useTheme'

const DIVISIONS = [
  { value: 'bba', label: 'BBA', sub: 'Business' },
  { value: 'hld', label: 'HLD', sub: 'Holdings' },
  { value: 'sci', label: 'SCI', sub: 'Science' },
  { value: 'ss',  label: 'SS',  sub: 'Service'  },
  { value: 'thm', label: 'THM', sub: 'Theme'    },
  { value: 'faa', label: 'FAA', sub: 'Finance'  },
  { value: 'mba', label: 'MBA', sub: 'Mgmt'     },
  { value: 'mm',  label: 'MM',  sub: 'Media'    },
]
const POSITIONS = [
  { value: 'chief',    label: 'Chief'    },
  { value: 'chairman', label: 'Chairman' },
  { value: 'head',     label: 'Head'     },
]

const router           = useRouter()
const auth             = useAuthStore()
const themeCtrl        = useTheme()
const selectedRole     = ref<string | null>(null)
const selectedPosition = ref<string | null>(null)
const name             = ref('')
const loading          = ref(false)
const error            = ref('')

const jobTitlePreview = computed(() =>
  selectedRole.value
    ? selectedPosition.value ? `${selectedRole.value},${selectedPosition.value}` : selectedRole.value
    : ''
)

async function handleLogin() {
  if (!selectedRole.value || !name.value.trim()) return
  error.value = ''; loading.value = true
  try {
    const res = await draftLogin({ job_title: jobTitlePreview.value, name: name.value.trim() })
    auth.setUser(res.token, res, jobTitlePreview.value)
    router.push(isFA(res.role) ? '/finance' : '/budget')
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = msg ?? 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่'
  } finally { loading.value = false }
}
</script>

<style scoped>
@reference "../style.css";

.role-card {
  @apply flex items-center justify-between px-4 py-3 rounded-xl border border-border bg-surface2
         hover:border-accent/50 transition-all cursor-pointer text-left;
}
.role-card--active { @apply border-accent bg-accent/10; }

.div-card {
  @apply flex flex-col items-center justify-center py-3 px-2 rounded-xl border border-border bg-surface2
         hover:border-accent/50 transition-all cursor-pointer;
}
.div-card--active { @apply border-accent bg-accent/10; }

.pos-pill {
  @apply px-4 py-1.5 rounded-full border border-border text-xs text-muted
         hover:border-accent/50 hover:text-fg transition-all cursor-pointer bg-surface2;
}
.pos-pill--active { @apply border-accent text-accent bg-accent/10; }
</style>
