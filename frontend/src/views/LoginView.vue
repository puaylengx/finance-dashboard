<template>
  <div class="min-h-screen bg-[#0f1117] flex items-center justify-center px-4 py-10">
    <div class="w-full max-w-md animate-fade-in">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-[#6c8efb]/15 border border-[#6c8efb]/30 mb-4">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#6c8efb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
            <line x1="12" y1="12" x2="12" y2="16"/><line x1="10" y1="14" x2="14" y2="14"/>
          </svg>
        </div>
        <h1 class="text-xl font-bold text-[#e2e8f0]">Finance Dashboard</h1>
        <p class="text-sm text-[#8892b0] mt-1">เลือกหน่วยงานและตำแหน่งเพื่อเข้าสู่ระบบ</p>
      </div>

      <div class="rounded-2xl border border-[#2e3250] bg-[#1a1d27] p-6 flex flex-col gap-6">

        <!-- Step 1: Role -->
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="w-5 h-5 rounded-full bg-[#6c8efb]/20 border border-[#6c8efb]/40 text-[#6c8efb] text-xs flex items-center justify-center font-semibold">1</span>
            <span class="text-sm font-medium text-[#e2e8f0]">เลือกหน่วยงาน</span>
          </div>

          <!-- FA special card -->
          <div class="mb-3">
            <button
              type="button"
              @click="selectedRole = 'fa'"
              class="role-card w-full"
              :class="selectedRole === 'fa' ? 'role-card--active' : ''"
            >
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
                  :class="selectedRole === 'fa' ? 'bg-[#6c8efb]/25' : 'bg-[#22263a]'">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    class="transition-colors" :class="selectedRole === 'fa' ? 'text-[#6c8efb]' : 'text-[#8892b0]'">
                    <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
                  </svg>
                </div>
                <div class="text-left">
                  <div class="text-sm font-semibold" :class="selectedRole === 'fa' ? 'text-[#6c8efb]' : 'text-[#e2e8f0]'">FA</div>
                  <div class="text-xs text-[#8892b0]">Finance &amp; Accounting</div>
                </div>
              </div>
              <div v-if="selectedRole === 'fa'" class="w-4 h-4 rounded-full bg-[#6c8efb] flex items-center justify-center shrink-0">
                <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
              </div>
            </button>
          </div>

          <!-- Division grid -->
          <div class="grid grid-cols-4 gap-2">
            <button
              v-for="div in DIVISIONS" :key="div.value"
              type="button"
              @click="selectedRole = div.value"
              class="div-card"
              :class="selectedRole === div.value ? 'div-card--active' : ''"
            >
              <div class="text-sm font-bold leading-tight" :class="selectedRole === div.value ? 'text-[#6c8efb]' : 'text-[#e2e8f0]'">{{ div.label }}</div>
              <div class="text-[10px] leading-tight mt-0.5" :class="selectedRole === div.value ? 'text-[#6c8efb]/70' : 'text-[#8892b0]'">{{ div.sub }}</div>
            </button>
          </div>
        </div>

        <!-- Step 2: Position (optional) -->
        <Transition name="slide-up">
          <div v-if="selectedRole">
            <div class="flex items-center gap-2 mb-3">
              <span class="w-5 h-5 rounded-full bg-[#6c8efb]/20 border border-[#6c8efb]/40 text-[#6c8efb] text-xs flex items-center justify-center font-semibold">2</span>
              <span class="text-sm font-medium text-[#e2e8f0]">ตำแหน่ง</span>
              <span class="text-xs text-[#8892b0]">(ถ้ามี)</span>
            </div>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="pos in POSITIONS" :key="pos.value"
                type="button"
                @click="selectedPosition = selectedPosition === pos.value ? null : pos.value"
                class="pos-pill"
                :class="selectedPosition === pos.value ? 'pos-pill--active' : ''"
              >{{ pos.label }}</button>
            </div>
          </div>
        </Transition>

        <!-- Step 3: Name -->
        <Transition name="slide-up">
          <div v-if="selectedRole">
            <div class="flex items-center gap-2 mb-3">
              <span class="w-5 h-5 rounded-full bg-[#6c8efb]/20 border border-[#6c8efb]/40 text-[#6c8efb] text-xs flex items-center justify-center font-semibold">3</span>
              <span class="text-sm font-medium text-[#e2e8f0]">ชื่อ-นามสกุล</span>
            </div>
            <input
              v-model="name"
              type="text"
              placeholder="กรอกชื่อ-นามสกุล"
              class="w-full bg-[#22263a] border border-[#2e3250] rounded-xl px-4 py-2.5 text-sm text-[#e2e8f0] outline-none placeholder:text-[#4a5568] focus:border-[#6c8efb] transition-colors"
              autocomplete="off"
              @keydown.enter="handleLogin"
            />
          </div>
        </Transition>

        <!-- Error -->
        <div v-if="error" class="text-xs text-[#f87171] rounded-lg border border-[#f87171]/30 bg-[#f87171]/10 px-3 py-2">
          {{ error }}
        </div>

        <!-- Summary + Submit -->
        <div v-if="selectedRole" class="flex items-center gap-3">
          <div class="flex-1 text-xs text-[#8892b0] bg-[#22263a] rounded-lg px-3 py-2 font-mono">
            {{ jobTitlePreview }}
          </div>
          <button
            type="button"
            :disabled="loading || !name.trim()"
            @click="handleLogin"
            class="px-5 py-2.5 rounded-xl bg-[#6c8efb] text-white text-sm font-medium hover:bg-[#5a7dea] transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
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

const DIVISIONS = [
  { value: 'bba', label: 'BBA', sub: 'Business' },
  { value: 'hld', label: 'HLD', sub: 'Holdings' },
  { value: 'sci', label: 'SCI', sub: 'Science' },
  { value: 'ss',  label: 'SS',  sub: 'Service' },
  { value: 'thm', label: 'THM', sub: 'Theme' },
  { value: 'faa', label: 'FAA', sub: 'Finance' },
  { value: 'mba', label: 'MBA', sub: 'Mgmt' },
  { value: 'mm',  label: 'MM',  sub: 'Media' },
]

const POSITIONS = [
  { value: 'chief',    label: 'Chief'    },
  { value: 'chairman', label: 'Chairman' },
  { value: 'head',     label: 'Head'     },
]

const router          = useRouter()
const auth            = useAuthStore()
const selectedRole    = ref<string | null>(null)
const selectedPosition = ref<string | null>(null)
const name            = ref('')
const loading         = ref(false)
const error           = ref('')

const jobTitlePreview = computed(() => {
  if (!selectedRole.value) return ''
  return selectedPosition.value
    ? `${selectedRole.value},${selectedPosition.value}`
    : selectedRole.value
})

async function handleLogin() {
  if (!selectedRole.value || !name.value.trim()) return
  error.value = ''
  loading.value = true
  try {
    const res = await draftLogin({ job_title: jobTitlePreview.value, name: name.value.trim() })
    auth.setUser(res.token, res, jobTitlePreview.value)
    router.push(isFA(res.role) ? '/finance' : '/budget')
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = msg ?? 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
@reference "../style.css";

.role-card {
  @apply flex items-center justify-between px-4 py-3 rounded-xl border border-[#2e3250] bg-[#22263a]
         hover:border-[#6c8efb]/50 hover:bg-[#22263a] transition-all cursor-pointer text-left;
}
.role-card--active {
  @apply border-[#6c8efb] bg-[#6c8efb]/10;
}

.div-card {
  @apply flex flex-col items-center justify-center py-3 px-2 rounded-xl border border-[#2e3250] bg-[#22263a]
         hover:border-[#6c8efb]/50 transition-all cursor-pointer;
}
.div-card--active {
  @apply border-[#6c8efb] bg-[#6c8efb]/10;
}

.pos-pill {
  @apply px-4 py-1.5 rounded-full border border-[#2e3250] text-xs text-[#8892b0]
         hover:border-[#6c8efb]/50 hover:text-[#e2e8f0] transition-all cursor-pointer bg-[#22263a];
}
.pos-pill--active {
  @apply border-[#6c8efb] text-[#6c8efb] bg-[#6c8efb]/10;
}
</style>
