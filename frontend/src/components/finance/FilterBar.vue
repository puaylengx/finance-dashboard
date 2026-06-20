<template>
  <div class="flex flex-wrap items-end gap-3 rounded-xl border border-border bg-surface p-4">
    <!-- Year mode toggle -->
    <div class="flex flex-col gap-1">
      <label class="text-xs text-muted">ประเภทปี</label>
      <div class="flex rounded-lg overflow-hidden border border-border">
        <button
          v-for="m in yearModes" :key="m.value"
          @click="filter.yearMode = m.value"
          class="px-3 py-2 text-xs transition-colors"
          :class="filter.yearMode === m.value ? 'bg-accent text-white' : 'bg-surface2 text-muted hover:text-fg'"
        >{{ m.label }}</button>
      </div>
    </div>

    <!-- Year -->
    <div class="flex flex-col gap-1">
      <label class="text-xs text-muted">{{ filter.yearMode === 'fiscal' ? 'ปีงบประมาณ' : 'PA Year' }}</label>
      <select v-model="selectedYear" class="input-select">
        <option v-for="y in yearList" :key="y" :value="y">{{ y }}</option>
      </select>
    </div>

    <!-- Month from -->
    <div class="flex flex-col gap-1">
      <label class="text-xs text-muted">เดือนเริ่ม</label>
      <select v-model="filter.monthFrom" class="input-select">
        <option :value="undefined">ทั้งหมด</option>
        <option v-for="m in 12" :key="m" :value="m">{{ fiscalMonthName(m) }}</option>
      </select>
    </div>

    <!-- Month to -->
    <div class="flex flex-col gap-1">
      <label class="text-xs text-muted">เดือนสิ้นสุด</label>
      <select v-model="filter.monthTo" class="input-select">
        <option :value="undefined">ทั้งหมด</option>
        <option v-for="m in 12" :key="m" :value="m">{{ fiscalMonthName(m) }}</option>
      </select>
    </div>

    <!-- Cost center -->
    <div class="flex flex-col gap-1 flex-1 min-w-36">
      <label class="text-xs text-muted">Cost Center</label>
      <input v-model="filter.costCenter" placeholder="เช่น H001" class="input-text" />
    </div>

    <!-- Search -->
    <div class="flex flex-col gap-1 flex-1 min-w-36">
      <label class="text-xs text-muted">ค้นหา</label>
      <input v-model="filter.q" placeholder="keyword..." class="input-text" />
    </div>

    <button
      @click="filter.resetFilters()"
      class="px-4 py-2 text-xs text-muted border border-border rounded-lg hover:text-fg hover:border-accent transition-colors self-end"
    >Reset</button>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useFilterStore } from '@/stores/filter'
import { fiscalMonthName } from '@/utils/format'

const filter = useFilterStore()
const yearModes = [{ label: 'Fiscal', value: 'fiscal' as const }, { label: 'PA', value: 'pa' as const }]
const currentYear = new Date().getFullYear()
const yearList = Array.from({ length: 8 }, (_, i) => currentYear - i)

const selectedYear = computed({
  get: () => filter.yearMode === 'fiscal' ? filter.year : filter.paYear,
  set: (v: number) => { if (filter.yearMode === 'fiscal') filter.year = v; else filter.paYear = v },
})
</script>
<style scoped>
@reference "../../style.css";
.input-select, .input-text {
  @apply bg-surface2 border border-border rounded-lg px-3 py-2 text-xs text-fg outline-none
         focus:border-accent transition-colors w-full;
}
</style>
