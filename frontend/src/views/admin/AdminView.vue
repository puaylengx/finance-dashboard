<template>
  <AppLayout>
    <div class="flex flex-col gap-6 animate-fade-in max-w-2xl">
      <div>
        <h2 class="text-lg font-semibold text-[#e2e8f0]">จัดการ Coordinators</h2>
        <p class="text-sm text-[#8892b0] mt-1">เพิ่ม / เปิด-ปิดสิทธิ์ coordinator</p>
      </div>

      <!-- Add form -->
      <form @submit.prevent="handleAdd" class="flex gap-3">
        <input
          v-model="newUsername" placeholder="username"
          class="flex-1 bg-[#22263a] border border-[#2e3250] rounded-xl px-4 py-2.5 text-sm text-[#e2e8f0] outline-none focus:border-[#6c8efb] transition-colors"
        />
        <button
          type="submit" :disabled="adding || !newUsername.trim()"
          class="px-5 py-2.5 rounded-xl bg-[#6c8efb] text-white text-sm font-medium hover:bg-[#5a7dea] transition-colors disabled:opacity-50"
        >
          {{ adding ? '...' : 'เพิ่ม' }}
        </button>
      </form>

      <div v-if="addError" class="text-xs text-[#f87171]">{{ addError }}</div>

      <!-- List -->
      <div class="rounded-xl border border-[#2e3250] bg-[#1a1d27] overflow-hidden">
        <template v-if="isPending">
          <div class="p-6 text-center text-sm text-[#8892b0]">กำลังโหลด...</div>
        </template>
        <template v-else-if="data?.length">
          <div
            v-for="c in data" :key="c.id"
            class="flex items-center justify-between px-5 py-4 border-b border-[#2e3250] last:border-0"
          >
            <div>
              <div class="text-sm text-[#e2e8f0]">{{ c.username }}</div>
              <div class="text-xs text-[#8892b0] mt-0.5">{{ c.created_at ? new Date(c.created_at).toLocaleDateString('th-TH') : '-' }}</div>
            </div>
            <button
              @click="handleToggle(c.id)"
              class="text-xs px-3 py-1.5 rounded-lg border transition-colors"
              :class="c.active
                ? 'border-[#34d399] text-[#34d399] hover:bg-[#34d399]/10'
                : 'border-[#8892b0] text-[#8892b0] hover:border-[#6c8efb] hover:text-[#6c8efb]'"
            >
              {{ c.active ? 'Active' : 'Inactive' }}
            </button>
          </div>
        </template>
        <div v-else class="p-6 text-center text-sm text-[#8892b0]">ยังไม่มี coordinator</div>
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
