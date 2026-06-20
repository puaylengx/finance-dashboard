<template>
  <AppLayout>
    <div class="flex flex-col gap-6 animate-fade-in max-w-2xl">
      <div>
        <h2 class="text-lg font-semibold text-fg">จัดการ Coordinators</h2>
        <p class="text-sm text-muted mt-1">เพิ่ม / เปิด-ปิดสิทธิ์ coordinator</p>
      </div>

      <!-- Add form -->
      <form @submit.prevent="handleAdd" class="flex gap-3">
        <input
          v-model="newUsername" placeholder="username"
          class="flex-1 bg-surface2 border border-border rounded-xl px-4 py-2.5 text-sm text-fg outline-none focus:border-accent transition-colors"
        />
        <button
          type="submit" :disabled="adding || !newUsername.trim()"
          class="px-5 py-2.5 rounded-xl bg-accent text-white text-sm font-medium hover:bg-accent-h transition-colors disabled:opacity-50"
        >
          {{ adding ? '...' : 'เพิ่ม' }}
        </button>
      </form>

      <div v-if="addError" class="text-xs text-danger">{{ addError }}</div>

      <!-- List -->
      <div class="rounded-xl border border-border bg-surface overflow-hidden">
        <template v-if="isPending">
          <div class="p-6 text-center text-sm text-muted">กำลังโหลด...</div>
        </template>
        <template v-else-if="data?.length">
          <div
            v-for="c in data" :key="c.id"
            class="flex items-center justify-between px-5 py-4 border-b border-border last:border-0"
          >
            <div>
              <div class="text-sm text-fg">{{ c.username }}</div>
              <div class="text-xs text-muted mt-0.5">{{ c.created_at ? new Date(c.created_at).toLocaleDateString('th-TH') : '-' }}</div>
            </div>
            <button
              @click="handleToggle(c.id)"
              class="text-xs px-3 py-1.5 rounded-lg border transition-colors"
              :class="c.active
                ? 'border-success text-success hover:bg-success/10'
                : 'border-muted text-muted hover:border-accent hover:text-accent'"
            >
              {{ c.active ? 'Active' : 'Inactive' }}
            </button>
          </div>
        </template>
        <div v-else class="p-6 text-center text-sm text-muted">ยังไม่มี coordinator</div>
      </div>
    </div>
  </AppLayout>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { fetchCoordinators, addCoordinator, toggleCoordinator } from '@/api/finance'
import AppLayout from '@/layouts/AppLayout.vue'

const qc = useQueryClient()

const { data, isPending } = useQuery({ queryKey: ['coordinators'], queryFn: fetchCoordinators })

const newUsername = ref('')
const adding      = ref(false)
const addError    = ref('')

const { mutate: mutateToggle } = useMutation({
  mutationFn: (id: number) => toggleCoordinator(id),
  onSuccess: () => qc.invalidateQueries({ queryKey: ['coordinators'] }),
})

async function handleAdd() {
  if (!newUsername.value.trim()) return
  addError.value = ''; adding.value = true
  try {
    await addCoordinator(newUsername.value.trim())
    newUsername.value = ''
    qc.invalidateQueries({ queryKey: ['coordinators'] })
  } catch (e: unknown) {
    addError.value = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'เพิ่มไม่สำเร็จ'
  } finally { adding.value = false }
}

const handleToggle = (id: number) => mutateToggle(id)
</script>
