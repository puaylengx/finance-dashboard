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
            <th class="px-4 py-3 font-medium">Code</th>
            <th class="px-4 py-3 font-medium">Description</th>
            <th class="px-4 py-3 font-medium text-right">Amount</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="item in rows" :key="item[idKey]">
            <tr
              class="border-t border-border bg-surface2 cursor-pointer hover:brightness-95 transition-all"
              @click="toggle(item[idKey])"
            >
              <td class="px-4 py-3 font-mono text-xs text-accent">{{ item[idKey] }}</td>
              <td class="px-4 py-3 text-fg">
                <span class="text-muted text-xs mr-1">{{ expanded.has(item[idKey]) ? '▾' : '▸' }}</span>
                {{ item[descKey] }}
              </td>
              <td class="px-4 py-3 text-right text-success">{{ fmt(item.total_amount) }}</td>
            </tr>
            <template v-if="expanded.has(item[idKey])">
              <tr v-for="d in item.order_breakdown" :key="d.details" class="border-t border-border bg-surface">
                <td class="px-4 py-2" />
                <td class="px-4 py-2 text-xs text-muted pl-10">{{ d.details }}</td>
                <td class="px-4 py-2 text-right text-xs text-fg">{{ fmt(d.amount) }}</td>
              </tr>
            </template>
          </template>
          <tr v-if="!rows.length">
            <td colspan="3" class="px-4 py-6 text-center text-muted">ไม่พบข้อมูล</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { fmt } from '@/utils/format'

interface BreakdownItem { details: string; amount: number }
interface Row { total_amount: number; order_breakdown: BreakdownItem[]; [key: string]: unknown }

defineProps<{
  title: string
  rows: Row[]
  idKey: string
  descKey: string
}>()
defineEmits<{ export: [] }>()

const expanded = ref(new Set<string>())
const toggle = (id: string) => expanded.value.has(id) ? expanded.value.delete(id) : expanded.value.add(id)
</script>
