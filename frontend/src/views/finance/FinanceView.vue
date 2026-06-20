<template>
  <AppLayout>
    <div class="flex flex-col gap-6 animate-fade-in">
      <FilterBar />

      <!-- Loading skeleton -->
      <template v-if="isPending">
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <SkeletonCard v-for="i in 4" :key="i" height="88px" />
        </div>
        <SkeletonCard height="280px" />
      </template>

      <!-- Error -->
      <div v-else-if="isError" class="rounded-xl border border-danger/30 bg-danger/10 p-5 text-sm text-danger">
        โหลดข้อมูลไม่สำเร็จ: {{ error?.message }}
      </div>

      <!-- Data -->
      <template v-else-if="data">
        <!-- KPIs -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard label="ยอดรวม (THB)" :value="data.kpis.total_amount" color="text-accent" />
          <KpiCard label="งบประมาณ (THB)" :value="data.kpis.total_budget" color="text-accent2" />
          <KpiCard label="จำนวนเอกสาร" :value="data.kpis.doc_count" color="text-success" />
          <KpiCard label="เฉลี่ย/เอกสาร" :value="data.kpis.avg_amount_per_doc" color="text-warning" />
        </div>

        <!-- Trend -->
        <TrendChart :items="data.trend_month" title="แนวโน้มรายเดือน" />

        <!-- Charts row -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <DonutChart
            :labels="data.table_by_gl.slice(0,8).map(r => r.gl_description)"
            :values="data.table_by_gl.slice(0,8).map(r => r.total)"
            title="สัดส่วน GL"
          />
          <DonutChart
            :labels="data.table_by_cost_center.slice(0,8).map(r => r.cost_center_description)"
            :values="data.table_by_cost_center.slice(0,8).map(r => r.total)"
            title="สัดส่วน Cost Center"
          />
        </div>

        <!-- GL Table -->
        <DataTable
          title="ตาม GL"
          :columns="glCols"
          :rows="glRows"
          @export="exportGl"
        />

        <!-- Pivot -->
        <PivotTable
          title="Pivot by GL Detail"
          :items="data.pivot_table_by_gl_detail"
          @export="exportPivot"
        />
      </template>
    </div>
  </AppLayout>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useFilterStore } from '@/stores/filter'
import { fetchFinance } from '@/api/finance'
import { fmt } from '@/utils/format'
import { exportCSV } from '@/utils/export'
import AppLayout   from '@/layouts/AppLayout.vue'
import FilterBar   from '@/components/finance/FilterBar.vue'
import KpiCard     from '@/components/ui/KpiCard.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import TrendChart  from '@/components/finance/TrendChart.vue'
import DonutChart  from '@/components/finance/DonutChart.vue'
import DataTable   from '@/components/finance/DataTable.vue'
import PivotTable  from '@/components/finance/PivotTable.vue'

const filter = useFilterStore()
const { data, isPending, isError, error } = useQuery({
  queryKey: computed(() => ['finance', filter.financeParams]),
  queryFn: () => fetchFinance(filter.financeParams),
  staleTime: 5 * 60_000,
})

const glCols = [
  { key: 'gl_id',          label: 'GL Code',      class: 'font-mono text-xs text-accent' },
  { key: 'gl_description', label: 'Description' },
  { key: 'gl_group',       label: 'Group',        class: 'text-muted text-xs' },
  { key: 'total',          label: 'Amount (THB)', class: 'text-right text-success', format: (v: unknown) => fmt(v as number) },
]
const glRows = computed(() => (data.value?.table_by_gl ?? []) as unknown as Record<string, unknown>[])

const exportGl    = () => exportCSV(glRows.value, 'finance_gl')
const exportPivot = () => exportCSV(
  (data.value?.pivot_table_by_gl_detail ?? []).map(r => ({ gl_id: r.gl_id, gl_description: r.gl_description, total_amount: r.total_amount })),
  'finance_pivot',
)
</script>
