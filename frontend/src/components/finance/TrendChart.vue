<template>
  <div class="rounded-xl border border-[#2e3250] bg-[#1a1d27] p-5">
    <div class="text-sm font-medium text-[#8892b0] mb-4">{{ title }}</div>
    <vue-apex-charts
      type="bar" height="240"
      :options="chartOptions" :series="series"
    />
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import type { TrendMonthItem } from '@/types/api'
import { fiscalMonthName } from '@/utils/format'

const props = defineProps<{ items: TrendMonthItem[]; title?: string }>()

const series = computed(() => [{
  name: 'Amount', data: props.items.map(i => Math.round(i.total)),
}])

const chartOptions = computed(() => ({
  chart:  { toolbar: { show: false }, background: 'transparent', fontFamily: 'inherit' },
  theme:  { mode: 'dark' as const },
  plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
  colors: ['#6c8efb'],
  dataLabels: { enabled: false },
  grid:   { borderColor: '#2e3250', strokeDashArray: 4 },
  xaxis:  { categories: props.items.map(i => fiscalMonthName(i.fiscal_month)), labels: { style: { colors: '#8892b0' } }, axisBorder: { show: false }, axisTicks: { show: false } },
  yaxis:  { labels: { style: { colors: '#8892b0' }, formatter: (v: number) => v >= 1_000_000 ? `${(v/1_000_000).toFixed(1)}M` : v >= 1_000 ? `${(v/1_000).toFixed(0)}K` : String(v) } },
  tooltip: { theme: 'dark' as const, y: { formatter: (v: number) => v.toLocaleString('th-TH') } },
}))
</script>
