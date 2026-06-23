<template>
  <AppLayout>
    <div class="flex flex-col gap-6 animate-fade-in">
      <div>
        <h2 class="text-lg font-semibold text-fg">จัดการ Coordinators</h2>
        <p class="text-sm text-muted mt-1">เพิ่ม / เปิด-ปิดสิทธิ์ coordinator</p>
      </div>

      <!-- Add form -->
      <form @submit.prevent="handleAdd" class="flex gap-3 max-w-md">
        <input
          v-model="newUsername" placeholder="username เช่น juntima.nuc"
          class="flex-1 bg-surface2 border border-border rounded-xl px-4 py-2.5 text-sm text-fg outline-none focus:border-accent transition-colors"
        />
        <button
          type="submit" :disabled="adding || !newUsername.trim()"
          class="px-5 py-2.5 rounded-xl bg-accent text-white text-sm font-medium hover:bg-accent-h transition-colors disabled:opacity-50"
        >
          {{ adding ? '...' : 'เพิ่ม' }}
        </button>
      </form>

      <!-- Table -->
      <div class="rounded-xl border border-border bg-surface overflow-hidden">
        <template v-if="isPending">
          <div class="p-6 text-center text-sm text-muted">กำลังโหลด...</div>
        </template>
        <template v-else-if="data?.length">
          <table class="w-full text-sm">
            <thead>
              <tr class="border-b border-border bg-surface2">
                <th
                  v-for="col in COLUMNS" :key="col.key"
                  class="text-left px-5 py-3 text-xs font-medium uppercase tracking-wide select-none"
                  :class="col.sortable
                    ? 'cursor-pointer text-muted hover:text-fg transition-colors'
                    : 'text-muted'"
                  @click="col.sortable && setSort(col.key)"
                >
                  <span class="inline-flex items-center gap-1">
                    {{ col.label }}
                    <template v-if="col.sortable">
                      <span v-if="sortKey === col.key" class="text-accent">
                        {{ sortDir === 'asc' ? '↑' : '↓' }}
                      </span>
                      <span v-else class="opacity-30">↕</span>
                    </template>
                  </span>
                </th>
                <th class="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="c in sorted" :key="c.id"
                class="border-b border-border last:border-0 hover:bg-surface2/50 transition-colors"
              >
                <td class="px-5 py-4 font-medium text-fg">{{ c.username }}</td>

                <!-- Status badge -->
                <td class="px-5 py-4">
                  <span
                    class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium"
                    :class="c.active ? 'bg-success/10 text-success' : 'bg-muted/10 text-muted'"
                  >
                    <span class="w-1.5 h-1.5 rounded-full" :class="c.active ? 'bg-success' : 'bg-muted'"></span>
                    {{ c.active ? 'Active' : 'Inactive' }}
                  </span>
                </td>

                <!-- Created info -->
                <td class="px-5 py-4">
                  <div class="text-fg">{{ c.created_by ?? '-' }}</div>
                  <div class="text-xs text-muted mt-0.5">{{ c.created_at ? fmtDate(c.created_at) : '-' }}</div>
                </td>

                <!-- Updated info -->
                <td class="px-5 py-4">
                  <template v-if="c.updated_by || c.updated_at">
                    <div class="text-fg">{{ c.updated_by ?? '-' }}</div>
                    <div class="text-xs text-muted mt-0.5">{{ c.updated_at ? fmtDate(c.updated_at) : '-' }}</div>
                  </template>
                  <span v-else class="text-xs text-muted">-</span>
                </td>

                <!-- Toggle action -->
                <td class="px-5 py-4 text-right">
                  <button
                    @click="handleToggle(c.id)"
                    class="text-xs px-3 py-1.5 rounded-lg border transition-colors"
                    :class="c.active
                      ? 'border-danger/40 text-danger hover:bg-danger/10'
                      : 'border-success/40 text-success hover:bg-success/10'"
                  >
                    {{ c.active ? 'ปิดสิทธิ์' : 'เปิดสิทธิ์' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </template>
        <div v-else class="p-6 text-center text-sm text-muted">ยังไม่มี coordinator</div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { fetchCoordinators, addCoordinator, toggleCoordinator } from '@/api/budget'
import type { CoordinatorResponse } from '@/types/api'
import AppLayout from '@/layouts/AppLayout.vue'
import { useToast } from '@/composables/useToast'

const qc    = useQueryClient()
const toast = useToast()

const { data, isPending } = useQuery({ queryKey: ['coordinators'], queryFn: fetchCoordinators })

const newUsername = ref('')

// ── Toggle: optimistic update ─────────────────────────────────────────────────
const { mutate: mutateToggle } = useMutation({
  mutationFn: (id: number) => toggleCoordinator(id),

  onMutate: async (id: number) => {
    await qc.cancelQueries({ queryKey: ['coordinators'] })
    const previous = qc.getQueryData<CoordinatorResponse[]>(['coordinators'])
    qc.setQueryData<CoordinatorResponse[]>(['coordinators'], old =>
      old?.map(c => c.id === id ? { ...c, active: !c.active } : c) ?? []
    )
    return { previous }
  },

  onError: (_err, _id, context) => {
    qc.setQueryData(['coordinators'], context?.previous)
    toast.error('ไม่สามารถเปลี่ยนสถานะได้ กรุณาลองใหม่')
  },

  onSettled: () => qc.invalidateQueries({ queryKey: ['coordinators'] }),
})

// ── Add: standard mutation with toast error ───────────────────────────────────
const { mutate: mutateAdd, isPending: adding } = useMutation({
  mutationFn: (username: string) => addCoordinator(username),
  onSuccess: () => {
    newUsername.value = ''
    qc.invalidateQueries({ queryKey: ['coordinators'] })
  },
  onError: (e: unknown) => {
    const detail = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    toast.error(detail ?? 'เพิ่มไม่สำเร็จ กรุณาลองใหม่')
  },
})

function handleAdd() {
  if (!newUsername.value.trim()) return
  mutateAdd(newUsername.value.trim())
}

const handleToggle = (id: number) => mutateToggle(id)

function fmtDate(iso: string) {
  const d = new Date(iso)
  const date = d.toLocaleDateString('th-TH', { day: 'numeric', month: 'long', year: 'numeric' })
  const time = d.toLocaleTimeString('th-TH', { hour: '2-digit', minute: '2-digit', hour12: false })
  return `${date} เวลา ${time} น.`
}

// Sort
type SortKey = 'username' | 'active' | 'created_at' | 'updated_at'
type SortDir = 'asc' | 'desc'

const COLUMNS: { key: SortKey | 'actions'; label: string; sortable: boolean }[] = [
  { key: 'username',   label: 'Username',      sortable: true },
  { key: 'active',     label: 'สถานะ',         sortable: true },
  { key: 'created_at', label: 'สร้างโดย',      sortable: true },
  { key: 'updated_at', label: 'อัปเดตล่าสุด', sortable: true },
]

const sortKey = ref<SortKey>('created_at')
const sortDir = ref<SortDir>('desc')

function setSort(key: SortKey | 'actions') {
  if (key === 'actions') return
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = key === 'username' || key === 'active' ? 'asc' : 'desc'
  }
}

const sorted = computed(() => {
  if (!data.value) return []
  return [...data.value].sort((a: CoordinatorResponse, b: CoordinatorResponse) => {
    let cmp = 0
    const k = sortKey.value
    if (k === 'username') {
      cmp = a.username.localeCompare(b.username, 'th')
    } else if (k === 'active') {
      cmp = Number(b.active) - Number(a.active)
    } else if (k === 'created_at') {
      cmp = (a.created_at ?? '').localeCompare(b.created_at ?? '')
    } else if (k === 'updated_at') {
      cmp = (a.updated_at ?? '').localeCompare(b.updated_at ?? '')
    }
    return sortDir.value === 'asc' ? cmp : -cmp
  })
})
</script>
