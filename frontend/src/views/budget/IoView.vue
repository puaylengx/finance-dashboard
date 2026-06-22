<template>
  <AppLayout>
    <div class="flex flex-col gap-6 animate-fade-in">
      <FilterBar :locked-cost-owner="lockedOwner" />

      <template v-if="isPending">
        <div class="grid grid-cols-3 gap-4">
          <SkeletonCard height="320px" />
          <div class="col-span-2"><SkeletonCard height="320px" /></div>
        </div>
        <div class="grid grid-cols-4 gap-4">
          <SkeletonCard height="120px" />
          <SkeletonCard height="120px" />
          <SkeletonCard height="120px" />
          <SkeletonCard height="120px" />
        </div>
        <SkeletonCard height="280px" />
      </template>

      <div v-else-if="isError" class="rounded-xl border border-danger/30 bg-danger/10 p-5 text-sm text-danger">
        โหลดข้อมูลไม่สำเร็จ: {{ error?.message }}
      </div>

      <template v-else-if="data">
        <!-- Row 1: KpiCards (1/3) + CostOwnerBarChart (2/3) -->
        <div class="grid grid-cols-3 gap-4">
          <div class="col-span-1 flex flex-col">
            <KpiCards :kpis="data.kpis" />
          </div>
          <div class="col-span-2 flex flex-col">
            <template v-if="auth.isUserFA">
              <div class="grid grid-cols-2 gap-4 flex-1">
                <CostOwnerBarChart :rows="data.spending_by_dept"     title="Top Cost Centers (Dept)"     class="h-full" />
                <CostOwnerBarChart :rows="data.spending_by_division" title="Top Cost Centers (Division)" class="h-full" />
              </div>
            </template>
            <CostOwnerBarChart v-else :rows="data.spending_by_all" title="Top Cost Centers" class="flex-1" />
          </div>
        </div>

        <!-- Row 2: IO type counts -->
        <div class="grid grid-cols-4 gap-4">
          <StatCard label="IO Goods" :value="fmtRound(data.kpis.count_io_goods)" unit="จำนวนรายการ" color="emerald">
            <template #icon>
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10" />
              </svg>
            </template>
          </StatCard>
          <StatCard label="IO Project" :value="fmtRound(data.kpis.count_io_project)" unit="จำนวนรายการ" color="violet">
            <template #icon>
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
              </svg>
            </template>
          </StatCard>
          <StatCard label="IO Activity" :value="fmtRound(data.kpis.count_io_activity)" unit="จำนวนรายการ" color="indigo">
            <template #icon>
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </template>
          </StatCard>
          <StatCard label="IO Work" :value="fmtRound(data.kpis.count_io_work)" unit="จำนวนรายการ" color="emerald">
            <template #icon>
              <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </template>
          </StatCard>
        </div>

        <!-- IO Goods -->
        <IoPivotTable
          title="IO Goods"
          :rows="data.pivot_table_by_io_goods"
          id-key="io_goods"
          desc-key="io_goods_description"
          @export="exportGoods"
        />

        <!-- IO Project -->
        <IoPivotTable
          title="IO Project"
          :rows="data.pivot_table_by_io_project"
          id-key="io_project"
          desc-key="io_project_description"
          @export="exportProject"
        />

        <!-- IO Activity -->
        <IoPivotTable
          title="IO Activity"
          :rows="data.pivot_table_by_io_activity"
          id-key="io_activity"
          desc-key="io_activity_description"
          @export="exportActivity"
        />

        <!-- IO Work -->
        <IoPivotTable
          title="IO Work"
          :rows="data.pivot_table_by_io_work"
          id-key="io_work"
          desc-key="io_work_description"
          @export="exportWork"
        />
      </template>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { useFilterStore } from '@/stores/filter'
import { useAuthStore } from '@/stores/auth'
import { fetchIO } from '@/api/budget'
import { fmtRound } from '@/utils/format'
import { exportCSV } from '@/utils/export'
import AppLayout    from '@/layouts/AppLayout.vue'
import FilterBar    from '@/components/budget/FilterBar.vue'
import SkeletonCard from '@/components/ui/SkeletonCard.vue'
import KpiCards     from '@/components/budget/KpiCards.vue'
import StatCard     from '@/components/budget/StatCard.vue'
import CostOwnerBarChart from '@/components/budget/CostOwnerBarChart.vue'
import IoPivotTable      from '@/components/budget/IoPivotTable.vue'

const filter      = useFilterStore()
const auth        = useAuthStore()
const lockedOwner = computed(() => auth.isUserFA ? undefined : auth.role)

const { data, isPending, isError, error } = useQuery({
  queryKey: computed(() => ['io', filter.ioParams]),
  queryFn: () => fetchIO(filter.ioParams),
  staleTime: 5 * 60_000,
})

const exportGoods    = () => exportCSV((data.value?.pivot_table_by_io_goods    ?? []).map(r => ({ id: r.io_goods,    desc: r.io_goods_description,    total: r.total_amount })), 'io_goods')
const exportProject  = () => exportCSV((data.value?.pivot_table_by_io_project  ?? []).map(r => ({ id: r.io_project,  desc: r.io_project_description,  total: r.total_amount })), 'io_project')
const exportActivity = () => exportCSV((data.value?.pivot_table_by_io_activity ?? []).map(r => ({ id: r.io_activity, desc: r.io_activity_description, total: r.total_amount })), 'io_activity')
const exportWork     = () => exportCSV((data.value?.pivot_table_by_io_work     ?? []).map(r => ({ id: r.io_work,     desc: r.io_work_description,     total: r.total_amount })), 'io_work')
</script>
