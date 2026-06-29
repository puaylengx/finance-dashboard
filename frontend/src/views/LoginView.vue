<template>
  <div class="min-h-screen bg-bg flex items-center justify-center px-4 py-10">

    <!-- Theme toggle -->
    <button
      @click="themeCtrl.toggle()"
      class="fixed top-4 right-4 w-9 h-9 rounded-xl border border-border bg-surface flex items-center justify-center text-muted hover:text-fg hover:border-accent transition-colors z-10"
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

    <div class="w-full max-w-lg animate-fade-in">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-accent/15 border border-accent/30 mb-4">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="2" y="7" width="20" height="14" rx="2"/><path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>
            <line x1="12" y1="12" x2="12" y2="16"/><line x1="10" y1="14" x2="14" y2="14"/>
          </svg>
        </div>
        <h1 class="text-xl font-bold text-fg">Finance Dashboard</h1>
        <p class="text-sm text-muted mt-1">
          {{ hasMsal ? 'เข้าสู่ระบบด้วยบัญชี Microsoft องค์กร' : 'เลือกหน่วยงานและตำแหน่งเพื่อเข้าสู่ระบบ' }}
        </p>
      </div>

      <!-- Session expired banner -->
      <div v-if="sessionExpired" class="flex items-start gap-3 rounded-xl border border-yellow-500/30 bg-yellow-500/10 px-4 py-3 mb-2">
        <svg class="shrink-0 mt-0.5" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#fbbf24" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <p class="text-xs text-yellow-400 leading-relaxed">Session หมดอายุ กรุณาเข้าสู่ระบบใหม่</p>
      </div>

      <div class="rounded-2xl border border-border bg-surface p-6 flex flex-col gap-6">

        <!-- Microsoft Login -->
        <div v-if="hasMsal" class="flex flex-col gap-3">
          <button
            type="button" :disabled="loading" @click="() => handleMicrosoftLogin()"
            class="flex items-center justify-center gap-3 w-full py-3 rounded-xl border border-border bg-surface2 hover:border-accent/60 hover:bg-accent/5 transition-all text-sm font-medium text-fg disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <!-- Microsoft logo -->
            <svg width="16" height="16" viewBox="0 0 21 21" fill="none">
              <rect x="1" y="1" width="9" height="9" fill="#f25022"/>
              <rect x="11" y="1" width="9" height="9" fill="#7fba00"/>
              <rect x="1" y="11" width="9" height="9" fill="#00a4ef"/>
              <rect x="11" y="11" width="9" height="9" fill="#ffb900"/>
            </svg>
            {{ loading && !showDraftForm ? 'กำลังเชื่อมต่อ...' : 'เข้าสู่ระบบด้วย Microsoft' }}
          </button>
        </div>

        <!-- Divider (MSAL + draft mode) -->
        <div v-if="hasMsal && isDraft" class="flex items-center gap-3 -my-2">
          <div class="flex-1 border-t border-border" />
          <button
            type="button" @click="showDraftForm = !showDraftForm"
            class="text-xs text-muted hover:text-fg transition-colors px-2 shrink-0"
          >
            {{ showDraftForm ? '▲ ซ่อน' : '▼ เข้าสู่ระบบแบบทดสอบ' }}
          </button>
          <div class="flex-1 border-t border-border" />
        </div>

        <!-- Draft Login Form -->
        <template v-if="showDraftForm">

        <!-- Step 1: เลือกหน่วยงาน -->
        <div>
          <div class="flex items-center gap-2 mb-3">
            <span class="step-badge">1</span>
            <span class="text-sm font-medium text-fg">เลือกหน่วยงาน</span>
          </div>

          <!-- FA card -->
          <button type="button" @click="selectFA" class="role-card w-full" :class="isFASelected ? 'role-card--active' : ''">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" :class="isFASelected ? 'bg-accent/25' : 'bg-surface2'">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                  :class="isFASelected ? 'text-accent' : 'text-muted'">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
                </svg>
              </div>
              <div class="text-left">
                <div class="text-sm font-semibold" :class="isFASelected ? 'text-accent' : 'text-fg'">FA</div>
                <div class="text-xs text-muted">Finance &amp; Accounting — Full Access</div>
              </div>
            </div>
            <div v-if="isFASelected" class="w-4 h-4 rounded-full bg-accent flex items-center justify-center shrink-0">
              <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </button>
          <!-- FA position -->
          <div v-if="isFASelected" class="flex gap-2 mt-2 mb-3">
            <button
              v-for="pos in STAFF_POSITIONS" :key="pos.value"
              type="button"
              @click="selectedPosition = selectedPosition === pos.value ? null : pos.value"
              class="pos-pill" :class="selectedPosition === pos.value ? 'pos-pill--active' : ''"
            >{{ pos.label }}</button>
            <span class="pos-pill text-muted/50 cursor-default border-dashed" v-if="!selectedPosition">ไม่มีตำแหน่ง</span>
          </div>
          <div v-else class="mb-3" />

          <!-- Category tabs -->
          <div class="flex gap-2 mb-3">
            <button
              v-for="cat in CATEGORIES" :key="cat.value"
              type="button" @click="selectCategory(cat.value)"
              class="cat-tab flex-1" :class="category === cat.value ? 'cat-tab--active' : ''"
            >{{ cat.label }}</button>
          </div>

          <!-- Division grid -->
          <div v-if="category === 'division'" class="grid grid-cols-3 gap-2">
            <button
              v-for="d in DIVISION_LIST" :key="d.value"
              type="button" @click="selectedRole = d.value"
              class="div-card" :class="selectedRole === d.value ? 'div-card--active' : ''"
            >
              <div class="text-sm font-bold leading-tight" :class="selectedRole === d.value ? 'text-accent' : 'text-fg'">{{ d.label }}</div>
              <div class="text-[10px] leading-tight mt-0.5" :class="selectedRole === d.value ? 'text-accent/70' : 'text-muted'">{{ d.sub }}</div>
            </button>
          </div>

          <!-- Staff grid -->
          <div v-if="category === 'staff'">
            <div class="grid grid-cols-5 gap-2 mb-3">
              <button
                v-for="s in STAFF_LIST" :key="s.value"
                type="button" @click="selectedRole = s.value"
                class="div-card" :class="selectedRole === s.value ? 'div-card--active' : ''"
              >
                <div class="text-sm font-bold" :class="selectedRole === s.value ? 'text-accent' : 'text-fg'">{{ s.label }}</div>
              </button>
            </div>
            <!-- Staff position -->
            <div v-if="selectedRole" class="flex gap-2">
              <button
                v-for="pos in STAFF_POSITIONS" :key="pos.value"
                type="button"
                @click="selectedPosition = selectedPosition === pos.value ? null : pos.value"
                class="pos-pill" :class="selectedPosition === pos.value ? 'pos-pill--active' : ''"
              >{{ pos.label }}</button>
              <span class="pos-pill text-muted/50 cursor-default border-dashed" v-if="!selectedPosition">ไม่มีตำแหน่ง</span>
            </div>
          </div>

          <!-- Faculty -->
          <div v-if="category === 'faculty'">
            <!-- Faculty roles (FT only) -->
            <div class="grid grid-cols-4 gap-2">
              <button
                v-for="r in FACULTY_ROLES" :key="r.value"
                type="button" @click="selectedRole = r.value"
                class="div-card" :class="selectedRole === r.value ? 'div-card--active' : ''"
              >
                <div class="text-sm font-bold" :class="selectedRole === r.value ? 'text-accent' : 'text-fg'">{{ r.label }}</div>
              </button>
            </div>
            <div v-if="selectedRole" class="mt-2">
              <span class="inline-flex items-center gap-1 text-xs text-accent bg-accent/10 border border-accent/30 rounded-full px-3 py-1">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
                Chairman
              </span>
            </div>
          </div>
        </div>

        <!-- Step 2: ชื่อ -->
        <Transition name="slide-up">
          <div v-if="jobTitlePreview">
            <div class="flex items-center gap-2 mb-3">
              <span class="step-badge">2</span>
              <span class="text-sm font-medium text-fg">ชื่อ-นามสกุล</span>
            </div>
            <input
              v-model="name" type="text" placeholder="กรอกชื่อ-นามสกุล"
              class="w-full bg-surface2 border border-border rounded-xl px-4 py-2.5 text-sm text-fg outline-none placeholder:text-placeholder focus:border-accent transition-colors"
              autocomplete="off" @keydown.enter="handleDraftLogin"
            />
          </div>
        </Transition>

        <!-- Draft: Error + Submit -->
        <div v-if="error && showDraftForm" class="text-xs text-danger rounded-lg border border-danger/30 bg-danger/10 px-3 py-2">
          {{ error }}
        </div>

        <div v-if="jobTitlePreview" class="flex items-center gap-3">
          <div class="flex-1 text-xs text-muted bg-surface2 rounded-lg px-3 py-2 font-mono truncate">
            {{ jobTitlePreview }}
          </div>
          <button
            type="button" :disabled="loading || !name.trim()" @click="handleDraftLogin"
            class="px-5 py-2.5 rounded-xl bg-accent text-white text-sm font-medium hover:bg-accent-h transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
          >
            {{ loading ? '...' : 'เข้าสู่ระบบ' }}
          </button>
        </div>

        </template><!-- end draft form -->

        <!-- MS Login error (shared) -->
        <div v-if="error && !showDraftForm" class="text-xs text-danger rounded-lg border border-danger/30 bg-danger/10 px-3 py-2">
          {{ error }}
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { draftLogin, entraLogin } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'
import { useTheme } from '@/composables/useTheme'
import { msalInstance, loginScopes, isMsalConfigured } from '@/lib/msalConfig'

const hasMsal  = isMsalConfigured()
const isDraft  = import.meta.env.VITE_DRAFT_MODE === 'true'
const showDraftForm = ref(!hasMsal)

type Category = 'division' | 'staff' | 'faculty'

const CATEGORIES = [
  { value: 'division' as Category, label: 'Division' },
  { value: 'staff'    as Category, label: 'Staff'    },
  { value: 'faculty'  as Category, label: 'Faculty'  },
]

const DIVISION_LIST = [
  { value: 'ba',  label: 'BA',  sub: 'Business' },
  { value: 'faa', label: 'FAA', sub: 'Finance'  },
  { value: 'hld', label: 'HLD', sub: 'Holdings' },
  { value: 'sci', label: 'SCI', sub: 'Science'  },
  { value: 'ss',  label: 'SS',  sub: 'Service'  },
  { value: 'thm', label: 'THM', sub: 'Theme'    },
]

const STAFF_LIST = [
  { value: 'ab', label: 'AB' }, { value: 'ar', label: 'AR' },
  { value: 'as', label: 'AS' }, { value: 'ca', label: 'CA' },
  { value: 'cc', label: 'CC' }, { value: 'ea', label: 'EA' },
  { value: 'ed', label: 'ED' }, { value: 'fa', label: 'FA' },
  { value: 'gp', label: 'GP' }, { value: 'hr', label: 'HR' },
  { value: 'ia', label: 'IA' }, { value: 'it', label: 'IT' },
  { value: 'ls', label: 'LS' }, { value: 'oe', label: 'OE' },
  { value: 'op', label: 'OP' }, { value: 'pc', label: 'PC' },
  { value: 'pe', label: 'PE' }, { value: 'ps', label: 'PS' },
  { value: 'rm', label: 'RM' }, { value: 'sa', label: 'SA' },
  { value: 'sd', label: 'SD' },
]

const STAFF_POSITIONS = [
  { value: 'chief', label: 'Chief' },
  { value: 'head',  label: 'Head'  },
]

const FACULTY_ROLES = [
  { value: 'ba', label: 'BA' }, { value: 'fa', label: 'FA' },
  { value: 'hl', label: 'HL' }, { value: 'sc', label: 'SC' },
  { value: 'ss', label: 'SS' }, { value: 'th', label: 'TH' },
]

const router           = useRouter()
const route            = useRoute()
const auth             = useAuthStore()
const sessionExpired   = computed(() => route.query.reason === 'session_expired')
const themeCtrl        = useTheme()
const isFASelected     = ref(false)
const category         = ref<Category | null>(null)
const selectedRole     = ref<string | null>(null)
const selectedPosition = ref<string | null>(null)
const name             = ref('')
const loading          = ref(false)
const error            = ref('')

const jobTitlePreview = computed(() => {
  if (isFASelected.value) return selectedPosition.value ? `fa,${selectedPosition.value}` : 'fa'
  if (!selectedRole.value) return ''
  if (category.value === 'division') return `staff,${selectedRole.value}`
  if (category.value === 'staff')
    return selectedPosition.value
      ? `staff,${selectedRole.value},${selectedPosition.value}`
      : `staff,${selectedRole.value}`
  if (category.value === 'faculty' && selectedRole.value) {
    return `faculty,ft_lecturers,${selectedRole.value},chairman`
  }
  return ''
})

function selectFA() {
  isFASelected.value     = true
  category.value         = null
  selectedRole.value     = null
  selectedPosition.value = null
}

function selectCategory(cat: Category) {
  isFASelected.value     = false
  category.value         = cat
  selectedRole.value     = null
  selectedPosition.value = null
}

watch(selectedRole, () => { selectedPosition.value = null })

async function handleDraftLogin() {
  if (!jobTitlePreview.value || !name.value.trim()) return
  error.value = ''; loading.value = true
  try {
    const res = await draftLogin({ job_title: jobTitlePreview.value, name: name.value.trim() })
    auth.setUser(res.token, res, name.value.trim())
    router.push('/budget')
  } catch (e: unknown) {
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    error.value = msg ?? 'เข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่'
  } finally { loading.value = false }
}

async function fetchJobTitleFromGraph(account: import('@azure/msal-browser').AccountInfo): Promise<string> {
  try {
    const graphResult = await msalInstance.acquireTokenSilent({
      scopes: ['https://graph.microsoft.com/User.Read'],
      account,
    })
    const resp = await fetch(
      'https://graph.microsoft.com/v1.0/me?$select=jobTitle',
      { headers: { Authorization: `Bearer ${graphResult.accessToken}` } },
    )
    if (!resp.ok) return ''
    const profile = await resp.json()
    return profile.jobTitle ?? ''
  } catch {
    return ''
  }
}

async function handleMicrosoftLogin(isRetry = false) {
  error.value = ''; loading.value = true
  try {
    const result = await msalInstance.loginPopup({
      ...loginScopes,
      redirectUri: `${window.location.origin}/auth-redirect.html`,
      prompt: 'select_account',
    })
    console.log('[MSAL] popup ok, account:', result.account?.username, 'token len:', result.accessToken.length)
    const jobTitle = result.account ? await fetchJobTitleFromGraph(result.account) : ''
    console.log('[MSAL] jobTitle from Graph:', jobTitle || '(empty)')
    const session = await entraLogin(result.accessToken, jobTitle)
    console.log('[MSAL] backend ok, role:', session.role)
    auth.setUser(session.token, session, result.account?.username ?? result.account?.name ?? '')
    router.push('/budget')
  } catch (e: unknown) {
    const errorCode = (e as { errorCode?: string })?.errorCode
    if (errorCode === 'user_cancelled') return
    if (errorCode === 'interaction_in_progress' && !isRetry) {
      Object.keys(sessionStorage)
        .filter(k => k.startsWith('msal.'))
        .forEach(k => sessionStorage.removeItem(k))
      loading.value = false
      await handleMicrosoftLogin(true)
      return
    }
    console.error('[MSAL] login error:', e)
    const backendMsg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    const rawMsg = (e as { message?: string })?.message ?? String(e)
    error.value = backendMsg ?? rawMsg
  } finally { loading.value = false }
}

</script>

<style scoped>
@reference "../style.css";

.step-badge {
  @apply w-5 h-5 rounded-full bg-accent/20 border border-accent/40 text-accent text-xs flex items-center justify-center font-semibold shrink-0;
}

.role-card {
  @apply flex items-center justify-between px-4 py-3 rounded-xl border border-border bg-surface2
         hover:border-accent/50 transition-all cursor-pointer text-left;
}
.role-card--active { @apply border-accent bg-accent/10; }

.cat-tab {
  @apply py-2 px-3 rounded-xl border border-border bg-surface2 text-sm text-muted
         hover:border-accent/50 hover:text-fg transition-all cursor-pointer font-medium;
}
.cat-tab--active { @apply border-accent text-accent bg-accent/10; }

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
