<template>
  <div class="rounded-xl border border-[#2e3250] bg-[#1a1d27] overflow-hidden">
    <div class="flex items-center justify-between px-5 py-4 border-b border-[#2e3250]">
      <div class="text-sm font-medium text-[#8892b0]">{{ title }}</div>
      <button @click="$emit('export')" class="text-xs text-[#6c8efb] hover:underline">Export CSV</button>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-[#8892b0] text-left">
            <th class="px-4 py-3 font-medium w-36">GL Code</th>
            <th class="px-4 py-3 font-medium">Description</th>
            <th class="px-4 py-3 font-medium text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="item in items" :key="item.gl_id">
            <tr
              class="border-t border-[#2e3250] bg-[#22263a] cursor-pointer hover:bg-[#2a2f4a] transition-colors"
              @click="toggle(item.gl_id)"
            >
              <td class="px-4 py-3 font-mono text-xs text-[#6c8efb]">{{ item.gl_id }}</td>
              <td class="px-4 py-3 text-[#e2e8f0] flex items-center gap-2">
                <span class="text-[#8892b0] text-xs">{{ expanded.has(item.gl_id) ? '▾' : '▸' }}</span>
                {{ item.gl_description }}
              </td>
              <td class="px-4 py-3 text-right text-[#34d399]">{{ fmt(item.total_amount) }}</td>
            </tr>
            <template v-if="expanded.has(item.gl_id)">
              <tr
                v-for="d in item.details_breakdown" :key="d.details"
                class="border-t border-[#2e3250] bg-[#1a1d27]"
              >
                <td class="px-4 py-2" />
                <td class="px-4 py-2 text-xs text-[#8892b0] pl-10">{{ d.details }}</td>
                <td class="px-4 py-2 text-right text-xs text-[#e2e8f0]">{{ fmt(d.amount) }}</td>
              </tr>
            </template>
          </template>
          <tr v-if="!items.length">
            <td colspan="3" class="px-4 py-6 text-center text-[#8892b0]">ไม่พบข้อมูล</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import type { PivotGlItem } from '@/types/api'
import { fmt } from '@/utils/format'

defineProps<{ title?: string; items: PivotGlItem[] }>()
defineEmits<{ (e: 'export'): void }>()

const expanded = ref(new Set<string>())
const toggle = (id: string) => expanded.value.has(id) ? expanded.value.delete(id) : expanded.value.add(id)
</script>
