<template>
  <div class="flex flex-wrap items-end gap-3 rounded-xl border border-[#2e3250] bg-[#1a1d27] p-4">
    <!-- Year mode toggle -->
    <div class="flex flex-col gap-1">
      <label class="text-xs text-[#8892b0]">ประเภทปี</label>
      <div class="flex rounded-lg overflow-hidden border border-[#2e3250]">
        <button
          v-for="m in yearModes" :key="m.value"
          @click="filter.yearMode = m.value"
          class="px-3 py-2 text-xs transition-colors"
          :class="filter.yearMode === m.value ? 'bg-[#6c8efb] text-white' : 'bg-[#22263a] text-[#8892b0] hover:text-[#e2e8f0]'"
        >{{ m.label }}</button>
      </div>
    </div>

    <!-- Year -->
    <div class="flex flex-col gap-1">
      <label class="text-xs text-[#8892b0]">{{ filter.yearMode === 'fiscal' ? 'ปีงบประมาณ' : 'PA Year' }}</label>
      <select v-model="selectedYear" class="input-select">
        <option v-for="y in yearList" :key="y" :value="y">{{ y }}</option>
      </select>
    </div>

    <!-- Month from -->
    <div class="flex flex-col gap-1">
      <label class="text-xs text-[#8892b0]">เดือนเริ่ม</label>
      <select v-model="filter.monthFrom" class="input-select">
        <option :value="undefined">ทั้งหมด</option>
        <option v-for="m in 12" :key="m" :value="m">{{ fiscalMonthName(m) }}</option>
      </select>
    </div>

    <!-- Month to -->
    <div class="flex flex-col gap-1">
      <label class="text-xs text-[#8892b0]">เดือนสิ้นสุด</label>
      <select v-model="filter.monthTo" class="input-select">
        <option :value="undefined">ทั้งหมด</option>
        <option v-for="m in 12" :key="m" :value="m">{{ fiscalMonthName(m) }}</option>
      </select>
    </div>

    <!-- Cost center -->
    <div class="flex flex-col gap-1 flex-1 min-w-36">
      <label class="text-xs text-[#8892b0]">Cost Center</label>
      <input v-model="filter.costCenter" placeholder="เช่น H001" class="input-text" />
    </div>

    <!-- Search -->
    <div class="flex flex-col gap-1 flex-1 min-w-36">
      <label class="text-xs text-[#8892b0]">ค้นหา</label>
      <input v-model="filter.q" placeholder="keyword..." class="input-text" />
    </div>

    <button @click="filter.resetFilters()" class="px-4 py-2 text-xs text-[#8892b0] border border-[#2e3250] rounded-lg hover:text-[#e2e8f0] hover:border-[#6c8efb] transition-colors self-end">
      Reset
    </button>
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
  @apply bg-[#22263a] border border-[#2e3250] rounded-lg px-3 py-2 text-xs text-[#e2e8f0] outline-none
         focus:border-[#6c8efb] transition-colors w-full;
}
</style>
