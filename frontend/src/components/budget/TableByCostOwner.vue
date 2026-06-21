<script setup lang="ts">
import { ref, computed } from 'vue'
import { fmt } from '@/utils/format'

interface CostCenterRow { cost_center_eng: string; cost_center_description: string; total: number }

const props = withDefaults(defineProps<{ rows: CostCenterRow[] }>(), { rows: () => [] })

type SortDir = 'asc' | 'desc' | null
const sortCol = ref<'name' | 'total'>('total')
const sortDir = ref<SortDir>('desc')

function toggleSort(col: 'name' | 'total') {
  if (sortCol.value === col) {
    sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortCol.value = col
    sortDir.value = col === 'total' ? 'desc' : 'asc'
  }
}

const sorted = computed(() => {
  return [...props.rows].sort((a, b) => {
    const dir = sortDir.value === 'desc' ? -1 : 1
    if (sortCol.value === 'total') return dir * (a.total - b.total)
    const na = a.cost_center_description || a.cost_center_eng
    const nb = b.cost_center_description || b.cost_center_eng
    return dir * na.localeCompare(nb)
  })
})

function sortIcon(col: string) {
  if (sortCol.value !== col) return '⇅'
  return sortDir.value === 'desc' ? '▼' : '▲'
}
</script>

<template>
  <div class="bg-surface rounded-xl border border-border shadow-sm p-4">
    <div class="flex items-center gap-2 mb-3">
      <div class="w-6 h-6 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0">
        <svg class="w-3 h-3 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
        </svg>
      </div>
      <h2 class="text-sm font-semibold text-fg">By Cost Center</h2>
    </div>

    <div class="overflow-auto max-h-72">
      <table class="w-full text-sm">
        <thead class="text-[11px] font-semibold text-muted uppercase tracking-wide border-b border-border sticky top-0 bg-surface">
          <tr>
            <th
              class="py-2.5 text-left cursor-pointer select-none hover:text-fg transition-colors"
              @click="toggleSort('name')"
            >
              Cost Center
              <span class="ml-1 text-[10px]" :class="sortCol === 'name' ? 'text-indigo-500' : 'text-muted/40'">
                {{ sortIcon('name') }}
              </span>
            </th>
            <th
              class="py-2.5 text-right cursor-pointer select-none hover:text-fg transition-colors"
              @click="toggleSort('total')"
            >
              Total Amount (THB)
              <span class="ml-1 text-[10px]" :class="sortCol === 'total' ? 'text-indigo-500' : 'text-muted/40'">
                {{ sortIcon('total') }}
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in sorted" :key="row.cost_center_eng"
            class="border-b border-border hover:bg-surface2 transition-colors"
          >
            <td class="py-2.5 pr-3 text-xs text-fg font-medium">
              {{ row.cost_center_description || row.cost_center_eng }}
            </td>
            <td class="py-2.5 text-right tabular-nums text-xs font-medium text-fg">
              {{ fmt(row.total) }}
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td colspan="2" class="text-center text-muted py-8 text-sm">No data</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
