<script setup lang="ts">
import { ref, computed } from 'vue'
import { fmt } from '@/utils/format'

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type Row = Record<string, any>

const props = defineProps<{
  title: string
  rows: Row[]
  idKey: string
  descKey: string
}>()
defineEmits<{ export: [] }>()

const expanded = ref(new Set<string>())
const toggle = (id: string) => expanded.value.has(id) ? expanded.value.delete(id) : expanded.value.add(id)

type SortCol = 'id' | 'desc' | 'amount'
type SortDir = 'asc' | 'desc'

const sortCol = ref<SortCol>('id')
const sortDir = ref<SortDir>('asc')

function setSort(col: SortCol) {
  if (sortCol.value === col) {
    sortDir.value = sortDir.value === 'desc' ? 'asc' : 'desc'
  } else {
    sortCol.value = col
    sortDir.value = col === 'amount' ? 'desc' : 'asc'
  }
}

function sortIcon(col: SortCol) {
  if (sortCol.value !== col) return '⇅'
  return sortDir.value === 'desc' ? '▼' : '▲'
}

const sorted = computed(() => {
  return [...props.rows].sort((a: Row, b: Row) => {
    const dir = sortDir.value === 'desc' ? -1 : 1
    if (sortCol.value === 'amount') return dir * (a.total_amount - b.total_amount)
    if (sortCol.value === 'id') return dir * String(a[props.idKey]).localeCompare(String(b[props.idKey]))
    return dir * String(a[props.descKey]).localeCompare(String(b[props.descKey]))
  })
})
</script>

<template>
  <div class="bg-surface rounded-xl border border-border shadow-sm p-5">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-7 h-7 rounded-lg bg-slate-500/10 flex items-center justify-center shrink-0">
        <svg class="w-3.5 h-3.5 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
        </svg>
      </div>
      <h2 class="text-sm font-semibold text-fg flex-1">{{ title }}</h2>
      <button @click="$emit('export')" class="text-xs text-accent hover:underline">Export CSV</button>
    </div>

    <div v-if="!rows.length" class="text-center text-muted py-8 text-sm">No data</div>
    <div v-else class="overflow-auto max-h-96">
      <table class="w-full text-sm">
        <thead class="sticky top-0 bg-surface2">
          <tr class="text-left text-xs text-muted uppercase tracking-wide">
            <th class="py-2 px-3 w-6"></th>
            <th
              class="py-2 px-3 whitespace-nowrap cursor-pointer select-none hover:text-fg transition-colors"
              @click="setSort('id')"
            >
              Code
              <span class="ml-1 text-[10px]" :class="sortCol === 'id' ? 'text-accent' : 'text-muted/40'">
                {{ sortIcon('id') }}
              </span>
            </th>
            <th
              class="py-2 px-3 cursor-pointer select-none hover:text-fg transition-colors"
              @click="setSort('desc')"
            >
              Description
              <span class="ml-1 text-[10px]" :class="sortCol === 'desc' ? 'text-accent' : 'text-muted/40'">
                {{ sortIcon('desc') }}
              </span>
            </th>
            <th
              class="py-2 px-3 text-right whitespace-nowrap cursor-pointer select-none hover:text-fg transition-colors"
              @click="setSort('amount')"
            >
              Total Amount (THB)
              <span class="ml-1 text-[10px]" :class="sortCol === 'amount' ? 'text-accent' : 'text-muted/40'">
                {{ sortIcon('amount') }}
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          <template v-for="item in sorted" :key="item[idKey]">
            <!-- Parent row -->
            <tr
              :class="expanded.has(item[idKey]) ? 'border-t border-indigo-500/30 bg-indigo-500/5' : 'border-t border-border hover:bg-surface2'"
              class="cursor-pointer transition-colors"
              @click="toggle(item[idKey])"
            >
              <td class="py-2 px-3 text-muted text-xs select-none">{{ expanded.has(item[idKey]) ? '▾' : '▸' }}</td>
              <td class="py-2 px-3 font-mono text-accent font-medium">{{ item[idKey] }}</td>
              <td class="py-2 px-3 text-fg font-medium">{{ item[descKey] }}</td>
              <td class="py-2 px-3 text-right font-semibold text-fg">{{ fmt(item.total_amount) }}</td>
            </tr>
            <!-- Expanded detail rows -->
            <tr v-if="expanded.has(item[idKey])" class="border-t border-indigo-500/20 bg-indigo-500/5">
              <td colspan="4" class="px-3 py-2">
                <div class="overflow-y-auto max-h-64">
                  <table class="w-full">
                    <tbody>
                      <tr v-for="d in item.order_breakdown" :key="d.details"
                        class="border-b border-indigo-500/10 last:border-0">
                        <td class="py-1.5 pl-4 text-xs text-fg w-full">{{ d.details || '—' }}</td>
                        <td class="py-1.5 pr-1 text-right text-xs text-fg font-medium whitespace-nowrap">{{ fmt(d.amount) }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>
