import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FinanceQueryParams, IoQueryParams } from '@/types/api'

const currentYear = new Date().getFullYear()

export const useFilterStore = defineStore('filter', () => {
  const yearMode   = ref<'fiscal' | 'pa'>('fiscal')
  const year       = ref(currentYear)
  const paYear     = ref(currentYear)
  const monthFrom  = ref<number | undefined>(undefined)
  const monthTo    = ref<number | undefined>(undefined)
  const costCenter = ref('')
  const costOwner  = ref('')
  const q          = ref('')

  const financeParams = computed((): FinanceQueryParams => ({
    year:        yearMode.value === 'fiscal' ? year.value : undefined,
    pa_year:     yearMode.value === 'pa'     ? paYear.value : undefined,
    month_from:  monthFrom.value,
    month_to:    monthTo.value,
    cost_center: costCenter.value || undefined,
    cost_owner:  costOwner.value  || undefined,
    q:           q.value          || undefined,
  }))

  const ioParams = computed((): IoQueryParams => ({
    year:        yearMode.value === 'fiscal' ? year.value : undefined,
    pa_year:     yearMode.value === 'pa'     ? paYear.value : undefined,
    month_from:  monthFrom.value,
    month_to:    monthTo.value,
    cost_center: costCenter.value || undefined,
    cost_owner:  costOwner.value  || undefined,
    q:           q.value          || undefined,
  }))

  function resetFilters() {
    monthFrom.value  = undefined
    monthTo.value    = undefined
    costCenter.value = ''
    q.value          = ''
  }

  return {
    yearMode, year, paYear, monthFrom, monthTo, costCenter, costOwner, q,
    financeParams, ioParams, resetFilters,
  }
})
