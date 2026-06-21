<template>
  <AppLayout title="Budget" show-export @export-excel="onExportExcel" @export-csv="onExportCsv" @print="printPage">
    <div class="space-y-4">
      <FilterBar show-cost-center />

      <!-- Loading -->
      <template v-if="isPending">
        <div class="grid grid-cols-3 gap-4">
          <SkeletonCard height="280px" />
          <div class="col-span-2"><SkeletonCard height="280px" /></div>
        </div>
        <SkeletonCard height="260px" />
      </template>

      <!-- Error -->
      <div v-else-if="isError" class="rounded-xl border border-danger/30 bg-danger/10 p-5 text-sm text-danger">
        โหลดข้อมูลไม่สำเร็จ: {{ error?.message }}
      </div>

      <template v-else-if="data">
        <!-- Row 1: KPI (1/3) + Quarterly (2/3) -->
        <div class="grid grid-cols-3 gap-4">
          <div class="col-span-1 flex flex-col">
            <KpiCards :kpis="data.kpis" />
          </div>
          <div class="col-span-2 flex flex-col">
            <QuarterBarChart :trend-data="data.trend_month ?? []" :year-type="filterStore.yearMode" />
          </div>
        </div>

        <!-- Row 2: Monthly Trend -->
        <TrendChart :items="data.trend_month ?? []" :year-type="filterStore.yearMode" />

        <!-- Division section -->
        <SectionHeader label="Division" />
        <div class="grid grid-cols-3 gap-4">
          <GlDonutChart
            :rows="data.table_by_gl_division ?? []"
            :chart-colors="DIVISION_COLORS"
            class="border-t-4 border-t-indigo-600"
          />
          <CostOwnerBarChart
            :rows="data.table_by_cost_center_division ?? []"
            class="border-t-4 border-t-indigo-600"
          />
          <TableByCostOwner
            :rows="data.table_by_cost_center_division ?? []"
            class="border-t-4 border-t-indigo-600"
          />
        </div>
        <PivotTable
          :items="data.pivot_table_by_gl_detail_division ?? []"
          class="border-t-4 border-t-indigo-600"
          @export="exportDivision"
        />

        <!-- Department section -->
        <SectionHeader label="Department" color="violet" top-padding="pt-3" />
        <div class="grid grid-cols-3 gap-4">
          <GlDonutChart
            :rows="data.table_by_gl ?? []"
            :chart-colors="DEPT_COLORS"
            class="border-t-4 border-t-violet-600"
          />
          <CostOwnerBarChart
            :rows="data.table_by_cost_center ?? []"
            bar-color="rgba(147, 51, 234, 0.85)"
            hover-color="rgba(147, 51, 234, 1)"
            class="border-t-4 border-t-violet-600"
          />
          <TableByCostOwner
            :rows="data.table_by_cost_center ?? []"
            class="border-t-4 border-t-violet-600"
          />
        </div>
        <PivotTable
          :items="data.pivot_table_by_gl_detail ?? []"
          class="border-t-4 border-t-violet-600"
          @export="exportDept"
        />
      </template>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useFilterStore } from '@/stores/filter'
import { fetchBudget } from '@/api/budget'
import { exportExcel, exportCSV, printPage } from '@/utils/export'
import { DIVISION_COLORS, DEPT_COLORS } from '@/utils/constants'

import AppLayout          from '@/layouts/AppLayout.vue'
import FilterBar          from '@/components/budget/FilterBar.vue'
import SkeletonCard       from '@/components/ui/SkeletonCard.vue'
import KpiCards           from '@/components/budget/KpiCards.vue'
import QuarterBarChart    from '@/components/budget/QuarterBarChart.vue'
import TrendChart         from '@/components/budget/TrendChart.vue'
import GlDonutChart       from '@/components/budget/GlDonutChart.vue'
import CostOwnerBarChart  from '@/components/budget/CostOwnerBarChart.vue'
import TableByCostOwner   from '@/components/budget/TableByCostOwner.vue'
import PivotTable         from '@/components/budget/PivotTable.vue'
import SectionHeader      from '@/components/ui/SectionHeader.vue'

const filterStore = useFilterStore()

const { data, isPending, isError, error } = useQuery({
  queryKey: computed(() => ['budget', filterStore.budgetParams]),
  queryFn:  () => fetchBudget(filterStore.budgetParams),
  staleTime: 5 * 60_000,
})

watch(data, d => {
  if (d && d.kpis.doc_count === 0 && filterStore.monthFrom !== undefined)
    filterStore.monthFrom = undefined
})

function onExportExcel() {
  if (!data.value) return
  exportExcel(
    data.value.pivot_table_by_gl_detail.map(r => ({
      'GL ID': r.gl_id, 'GL Description': r.gl_description, 'Total Amount': r.total_amount,
    })),
    'budget-report',
  )
}
function onExportCsv() {
  if (!data.value) return
  exportCSV(
    data.value.pivot_table_by_gl_detail.map(r => ({
      gl_id: r.gl_id, gl_description: r.gl_description, total_amount: r.total_amount,
    })),
    'budget-report',
  )
}
const exportDivision = () => {
  if (!data.value) return
  exportCSV(
    data.value.pivot_table_by_gl_detail_division.map(r => ({
      gl_id: r.gl_id, gl_description: r.gl_description, total_amount: r.total_amount,
    })),
    'budget-division',
  )
}
const exportDept = () => {
  if (!data.value) return
  exportCSV(
    data.value.pivot_table_by_gl_detail.map(r => ({
      gl_id: r.gl_id, gl_description: r.gl_description, total_amount: r.total_amount,
    })),
    'budget-dept',
  )
}
</script>
