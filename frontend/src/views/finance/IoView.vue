<template>
  <AppLayout>
    <div class="flex flex-col gap-6 animate-fade-in">
      <FilterBar />

      <template v-if="isPending">
        <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <SkeletonCard v-for="i in 6" :key="i" height="88px" />
        </div>
        <SkeletonCard height="280px" />
      </template>

      <div v-else-if="isError" class="rounded-xl border border-danger/30 bg-danger/10 p-5 text-sm text-danger">
        โหลดข้อมูลไม่สำเร็จ: {{ error?.message }}
      </div>

      <template v-else-if="data">
        <div class="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <KpiCard label="ยอดรวม (THB)"    :value="data.kpis.total_amount"          color="text-accent" />
          <KpiCard label="งบประมาณ (THB)"   :value="data.kpis.total_budget"          color="text-accent2" />
          <KpiCard label="IO Goods (THB)"   :value="data.kpis.total_amount_io_goods" color="text-success" />
          <KpiCard label="IO Project (THB)" :value="data.kpis.total_amount_io_project" color="text-warning" />
          <KpiCard label="จำนวน IO Goods"   :value="data.kpis.count_io_goods"        color="text-accent" />
          <KpiCard label="จำนวน IO Project" :value="data.kpis.count_io_project"      color="text-accent2" />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <DonutChart
            :labels="data.spending_by_dept.slice(0,8).map(r => r.cost_center_description)"
            :values="data.spending_by_dept.slice(0,8).map(r => r.total)"
            title="สัดส่วน (Dept)"
          />
          <DonutChart
            :labels="data.spending_by_division.slice(0,8).map(r => r.cost_center_description)"
            :values="data.spending_by_division.slice(0,8).map(r => r.total)"
            title="สัดส่วน (Division)"
          />
        </div>

        <!-- IO Goods Pivot -->
        <div class="rounded-xl border border-border bg-surface overflow-hidden">
          <div class="flex items-center justify-between px-5 py-4 border-b border-border">
            <div class="text-sm font-medium text-muted">IO Goods</div>
            <button @click="exportIoGoods" class="text-xs text-accent hover:underline">Export CSV</button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-sm">
              <thead>
                <tr class="text-muted text-left">
                  <th class="px-4 py-3 font-medium">IO Code</th>
                  <th class="px-4 py-3 font-medium">Description</th>
                  <th class="px-4 py-3 font-medium text-right">Amount</th>
                </tr>
              </thead>
              <tbody>
                <template v-for="item in data.pivot_table_by_io_goods" :key="item.io_goods">
                  <tr
                    class="border-t border-border bg-surface2 cursor-pointer hover:brightness-95 transition-all"
                    @click="toggleGoods(item.io_goods)"
                  >
                    <td class="px-4 py-3 font-mono text-xs text-accent">{{ item.io_goods }}</td>
                    <td class="px-4 py-3 text-fg">
                      <span class="text-muted text-xs mr-1">{{ expandedGoods.has(item.io_goods) ? '▾' : '▸' }}</span>
                      {{ item.io_goods_description }}
                    </td>
                    <td class="px-4 py-3 text-right text-success">{{ fmt(item.total_amount) }}</td>
                  </tr>
                  <template v-if="expandedGoods.has(item.io_goods)">
                    <tr v-for="d in item.order_breakdown" :key="d.details" class="border-t border-border bg-surface">
                      <td class="px-4 py-2" />
                      <td class="px-4 py-2 text-xs text-muted pl-10">{{ d.details }}</td>
                      <td class="px-4 py-2 text-right text-xs text-fg">{{ fmt(d.amount) }}</td>
                    </tr>
                  </template>
                </template>
                <tr v-if="!data.pivot_table_by_io_goods.length">
                  <td colspan="3" class="px-4 py-6 text-center text-muted">ไม่พบข้อมูล</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </div>
  </AppLayout>
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useFilterStore } from '@/stores/filter'
import { fetchIO } from '@/api/finance'
import { fmt } from '@/utils/format'
import { exportCSV } from '@/utils/export'
import AppLayout    from '@/layouts/AppLayout.vue'
import FilterBar    from '@/components/finance/FilterBar.vue'
import KpiCard      from '@/components/ui/KpiCard.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import DonutChart   from '@/components/finance/DonutChart.vue'

const filter = useFilterStore()
const { data, isPending, isError, error } = useQuery({
  queryKey: computed(() => ['io', filter.ioParams]),
  queryFn: () => fetchIO(filter.ioParams),
  staleTime: 5 * 60_000,
})

const expandedGoods = ref(new Set<string>())
const toggleGoods = (id: string) => expandedGoods.value.has(id) ? expandedGoods.value.delete(id) : expandedGoods.value.add(id)

const exportIoGoods = () => exportCSV(
  (data.value?.pivot_table_by_io_goods ?? []).map(r => ({ io_goods: r.io_goods, description: r.io_goods_description, total: r.total_amount })),
  'io_goods',
)
</script>
