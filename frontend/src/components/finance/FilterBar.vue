<script setup lang="ts">
import { reactive, computed, watch } from 'vue'
import { useFilterStore } from '@/stores/filter'
import { FISCAL_MONTHS, PA_MONTHS, fiscalMonthLabel, paMonthLabel } from '@/utils/constants'

type YearType = 'fiscal' | 'pa'

interface Filters {
  year:        number
  year_type:   YearType
  month_from:  number
  month_to:    number
  cost_center: string
  cost_owner:  string
  q:           string
}

const props = withDefaults(
  defineProps<{ showCostCenter?: boolean; lockedCostOwner?: string }>(),
  { showCostCenter: true },
)

const filterStore = useFilterStore()

function currentYear() { return new Date().getFullYear() }
function buildYearOptions(type: YearType) {
  return Array.from({ length: 11 }, (_, i) => currentYear() - 5 + i).map(y => {
    const label = type === 'pa'
      ? `PA ${y} (Jul ${y - 1} – Jun ${y})`
      : `FY ${y} (Oct ${y - 1} – Sep ${y})`
    return { value: y, label }
  })
}

const filters = reactive<Filters>({
  year:        filterStore.yearMode === 'pa' ? filterStore.paYear : filterStore.year,
  year_type:   filterStore.yearMode,
  month_from:  filterStore.monthFrom ?? 1,
  month_to:    filterStore.monthTo   ?? 12,
  cost_center: filterStore.costCenter,
  cost_owner:  props.lockedCostOwner ?? filterStore.costOwner,
  q:           filterStore.q,
})

const currentMonths = computed(() =>
  filters.year_type === 'pa' ? PA_MONTHS : FISCAL_MONTHS,
)
const currentMonthLabel = computed(() =>
  filters.year_type === 'pa' ? paMonthLabel : fiscalMonthLabel,
)
const yearOptions = computed(() => buildYearOptions(filters.year_type))

const activeChips = computed(() => {
  const opt      = yearOptions.value.find(o => o.value === filters.year)
  const chips: string[] = [opt?.label ?? String(filters.year)]
  const labelFn = currentMonthLabel.value
  if (filters.month_from !== 1 || filters.month_to !== 12)
    chips.push(`${labelFn(filters.month_from)} → ${labelFn(filters.month_to)}`)
  if (props.showCostCenter && filters.cost_center) chips.push(`CC: ${filters.cost_center}`)
  if (filters.cost_owner)                           chips.push(`Owner: ${filters.cost_owner}`)
  if (filters.q)                                    chips.push(`"${filters.q}"`)
  return chips
})

function syncToStore() {
  filterStore.yearMode    = filters.year_type
  filterStore.costCenter  = filters.cost_center
  filterStore.costOwner   = filters.cost_owner
  filterStore.q           = filters.q
  filterStore.monthFrom   = filters.month_from !== 1  ? filters.month_from  : undefined
  filterStore.monthTo     = filters.month_to   !== 12 ? filters.month_to    : undefined
  if (filters.year_type === 'pa') filterStore.paYear = filters.year
  else                            filterStore.year   = filters.year
}

watch(() => filters.year_type, type => {
  filters.month_from = 1
  filters.month_to   = 12
  filters.year       = currentYear() - (type === 'pa' ? 2 : 1)
})

watch(() => filters.month_to, val => {
  if (filters.month_from > val) { filters.month_from = 1; filters.month_to = 12 }
})

watch(() => filterStore.monthFrom, val => {
  filters.month_from = val ?? 1
})

let timer: ReturnType<typeof setTimeout> | null = null
watch(() => ({ ...filters }), () => {
  if (timer) clearTimeout(timer)
  timer = setTimeout(syncToStore, 350)
}, { deep: true })

function reset() {
  Object.assign(filters, {
    year:        currentYear() - 1,
    year_type:   'fiscal' as YearType,
    month_from:  1,
    month_to:    12,
    cost_center: '',
    cost_owner:  props.lockedCostOwner ?? '',
    q:           '',
  })
  if (timer) clearTimeout(timer)
  syncToStore()
}
</script>

<template>
  <div class="bg-surface rounded-xl border border-border shadow-sm px-5 py-4">
    <div class="flex flex-wrap gap-3 items-center">

      <!-- Year Type -->
      <div class="flex flex-col gap-1">
        <label class="text-[10px] font-semibold text-muted uppercase tracking-wider">Year Type</label>
        <div class="flex items-center gap-3 h-8">
          <label class="flex items-center gap-1.5 text-sm text-fg cursor-pointer select-none">
            <input type="radio" v-model="filters.year_type" value="fiscal"
              class="accent-indigo-600 w-3.5 h-3.5 cursor-pointer" />
            <span>ปีงบประมาณ</span>
          </label>
          <label class="flex items-center gap-1.5 text-sm text-fg cursor-pointer select-none">
            <input type="radio" v-model="filters.year_type" value="pa"
              class="accent-indigo-600 w-3.5 h-3.5 cursor-pointer" />
            <span>ปี PA</span>
          </label>
        </div>
      </div>

      <div class="h-8 w-px bg-border mx-0.5 self-center"></div>

      <!-- Year -->
      <div class="flex flex-col gap-1">
        <label class="text-[10px] font-semibold text-muted uppercase tracking-wider">Year</label>
        <select v-model="filters.year" class="filter-select">
          <option v-for="opt in yearOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
        </select>
      </div>

      <!-- Month From -->
      <div class="flex flex-col gap-1">
        <label class="text-[10px] font-semibold text-muted uppercase tracking-wider">From</label>
        <select v-model="filters.month_from" class="filter-select">
          <option v-for="m in currentMonths" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
      </div>

      <!-- Month To -->
      <div class="flex flex-col gap-1">
        <label class="text-[10px] font-semibold text-muted uppercase tracking-wider">To</label>
        <select v-model="filters.month_to" class="filter-select">
          <option v-for="m in currentMonths" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
      </div>

      <div class="h-8 w-px bg-border mx-0.5 self-center"></div>

      <!-- Cost Owner -->
      <div class="flex flex-col gap-1">
        <label class="text-[10px] font-semibold text-muted uppercase tracking-wider">Cost Owner</label>
        <div class="relative">
          <input
            v-model="filters.cost_owner"
            :placeholder="lockedCostOwner ? '' : 'ID or name'"
            :disabled="!!lockedCostOwner"
            class="filter-input w-32"
            :class="lockedCostOwner ? 'opacity-50 cursor-not-allowed pr-7' : ''"
          />
          <svg v-if="lockedCostOwner" class="absolute right-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
      </div>

      <!-- Cost Center -->
      <div v-if="showCostCenter" class="flex flex-col gap-1">
        <label class="text-[10px] font-semibold text-muted uppercase tracking-wider">Cost Center</label>
        <input v-model="filters.cost_center" placeholder="Search name..." class="filter-input w-36" />
      </div>

      <!-- Keyword -->
      <div class="flex flex-col gap-1">
        <label class="text-[10px] font-semibold text-muted uppercase tracking-wider">Keyword</label>
        <div class="relative">
          <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <input v-model="filters.q" placeholder="Search details..." class="filter-input w-40 pl-8" />
        </div>
      </div>

      <!-- Reset -->
      <div class="ml-auto self-center">
        <button @click="reset" class="h-8 px-4 text-sm text-muted border border-border rounded-lg hover:bg-surface2 hover:text-fg transition-colors bg-surface">
          Reset
        </button>
      </div>
    </div>

    <!-- Active filter chips -->
    <div class="flex items-center gap-2 pt-3 border-t border-border mt-3">
      <span class="text-[10px] font-semibold text-muted uppercase tracking-widest shrink-0">Filter:</span>
      <div class="flex flex-wrap gap-1.5">
        <span
          v-for="chip in activeChips" :key="chip"
          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-indigo-500/10 text-indigo-600 border border-indigo-500/20"
        >{{ chip }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "../../style.css";
.filter-select {
  @apply h-8 border border-border rounded-lg px-2.5 text-sm text-fg bg-surface2
         hover:border-accent/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition;
}
.filter-input {
  @apply h-8 border border-border rounded-lg px-2.5 text-sm text-fg bg-surface2
         hover:border-accent/60 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-400 transition;
}
</style>
