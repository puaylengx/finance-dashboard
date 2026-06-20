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
            <th v-for="col in columns" :key="col.key" class="px-4 py-3 font-medium">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, i) in rows" :key="i"
            class="border-t border-[#2e3250] hover:bg-[#22263a] transition-colors"
          >
            <td v-for="col in columns" :key="col.key" class="px-4 py-3" :class="col.class">
              {{ col.format ? col.format(row[col.key]) : row[col.key] }}
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td :colspan="columns.length" class="px-4 py-6 text-center text-[#8892b0]">ไม่พบข้อมูล</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<script setup lang="ts">
interface Column { key: string; label: string; class?: string; format?: (v: unknown) => string }
defineProps<{ title?: string; columns: Column[]; rows: Record<string, unknown>[] }>()
defineEmits<{ (e: 'export'): void }>()
</script>
