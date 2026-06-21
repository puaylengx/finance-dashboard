<script setup lang="ts">
import { ref } from 'vue'
import type { PivotGlItem } from '@/types/api'
import { fmt } from '@/utils/format'

defineProps<{ title?: string; items: PivotGlItem[] }>()
defineEmits<{ (e: 'export'): void }>()

const expanded = ref(new Set<string>())
const toggle   = (id: string) => expanded.value.has(id) ? expanded.value.delete(id) : expanded.value.add(id)
</script>

<template>
  <div class="bg-surface rounded-xl border border-border shadow-sm p-5">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-7 h-7 rounded-lg bg-slate-500/10 flex items-center justify-center shrink-0">
        <svg class="w-3.5 h-3.5 text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16"/>
        </svg>
      </div>
      <h2 class="text-sm font-semibold text-fg flex-1">GL Detail Breakdown</h2>
      <button @click="$emit('export')" class="text-xs text-accent hover:underline">Export CSV</button>
    </div>

    <div v-if="!items.length" class="text-center text-muted py-8 text-sm">No data</div>
    <div v-else class="overflow-auto max-h-96">
      <table class="w-full text-sm">
        <thead class="sticky top-0 bg-surface2">
          <tr class="text-left text-xs text-muted uppercase tracking-wide">
            <th class="py-2 px-3 w-6"></th>
            <th class="py-2 px-3 whitespace-nowrap">GL Code</th>
            <th class="py-2 px-3">Description</th>
            <th class="py-2 px-3 text-right whitespace-nowrap">Total Amount (THB)</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="item in items" :key="item.gl_id">
            <!-- Parent row -->
            <tr
              :class="expanded.has(item.gl_id) ? 'border-t border-indigo-500/30 bg-indigo-500/5' : 'border-t border-border hover:bg-surface2'"
              class="cursor-pointer transition-colors"
              @click="toggle(item.gl_id)"
            >
              <td class="py-2 px-3 text-muted text-xs select-none">{{ expanded.has(item.gl_id) ? '▾' : '▸' }}</td>
              <td class="py-2 px-3 font-mono text-accent font-medium">{{ item.gl_id }}</td>
              <td class="py-2 px-3 text-fg font-medium">{{ item.gl_description }}</td>
              <td class="py-2 px-3 text-right font-semibold text-fg">{{ fmt(item.total_amount) }}</td>
            </tr>
            <!-- Expanded detail rows -->
            <tr v-if="expanded.has(item.gl_id)" class="border-t border-indigo-500/20 bg-indigo-500/5">
              <td colspan="4" class="px-3 py-2">
                <div class="overflow-y-auto max-h-64">
                  <table class="w-full">
                    <tbody>
                      <tr v-for="(d, i) in item.details_breakdown" :key="i"
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
