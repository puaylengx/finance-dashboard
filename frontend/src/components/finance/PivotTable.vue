<template>
  <div class="rounded-xl border border-border bg-surface overflow-hidden">
    <div class="flex items-center justify-between px-5 py-4 border-b border-border">
      <div class="text-sm font-medium text-muted">{{ title }}</div>
      <button @click="$emit('export')" class="text-xs text-accent hover:underline">Export CSV</button>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="text-muted text-left">
            <th class="px-4 py-3 font-medium w-36">GL Code</th>
            <th class="px-4 py-3 font-medium">Description</th>
            <th class="px-4 py-3 font-medium text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="item in items" :key="item.gl_id">
            <tr
              class="border-t border-border bg-surface2 cursor-pointer hover:brightness-95 transition-all"
              @click="toggle(item.gl_id)"
            >
              <td class="px-4 py-3 font-mono text-xs text-accent">{{ item.gl_id }}</td>
              <td class="px-4 py-3 text-fg flex items-center gap-2">
                <span class="text-muted text-xs">{{ expanded.has(item.gl_id) ? '▾' : '▸' }}</span>
                {{ item.gl_description }}
              </td>
              <td class="px-4 py-3 text-right text-success">{{ fmt(item.total_amount) }}</td>
            </tr>
            <template v-if="expanded.has(item.gl_id)">
              <tr v-for="d in item.details_breakdown" :key="d.details" class="border-t border-border bg-surface">
                <td class="px-4 py-2" />
                <td class="px-4 py-2 text-xs text-muted pl-10">{{ d.details }}</td>
                <td class="px-4 py-2 text-right text-xs text-fg">{{ fmt(d.amount) }}</td>
              </tr>
            </template>
          </template>
          <tr v-if="!items.length">
            <td colspan="3" class="px-4 py-6 text-center text-muted">ไม่พบข้อมูล</td>
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
