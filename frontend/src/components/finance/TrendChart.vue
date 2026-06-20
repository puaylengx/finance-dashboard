<template>
  <div class="rounded-xl border border-border bg-surface p-5">
    <div class="text-sm font-medium text-muted mb-4">{{ title }}</div>
    <vue-apex-charts type="bar" height="240" :options="chartOptions" :series="series" />
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import type { TrendMonthItem } from '@/types/api'
import { fiscalMonthName } from '@/utils/format'
import { useTheme } from '@/composables/useTheme'

const props = defineProps<{ items: TrendMonthItem[]; title?: string }>()
const { theme } = useTheme()

const series = computed(() => [{ name: 'Amount', data: props.items.map(i => Math.round(i.total)) }])

const chartOptions = computed(() => {
  const dark = theme.value === 'dark'
  return {
    chart:  { toolbar: { show: false }, background: 'transparent', fontFamily: 'inherit' },
    theme:  { mode: (dark ? 'dark' : 'light') as 'dark' | 'light' },
    plotOptions: { bar: { borderRadius: 4, columnWidth: '60%' } },
    colors: ['#6c8efb'],
    dataLabels: { enabled: false },
    grid:   { borderColor: dark ? '#2e3250' : '#e2e8f0', strokeDashArray: 4 },
    xaxis:  {
      categories: props.items.map(i => fiscalMonthName(i.fiscal_month)),
      labels: { style: { colors: dark ? '#8892b0' : '#64748b' } },
      axisBorder: { show: false }, axisTicks: { show: false },
    },
    yaxis:  {
      labels: {
        style: { colors: dark ? '#8892b0' : '#64748b' },
        formatter: (v: number) => v >= 1_000_000 ? `${(v/1_000_000).toFixed(1)}M` : v >= 1_000 ? `${(v/1_000).toFixed(0)}K` : String(v),
      },
    },
    tooltip: { theme: (dark ? 'dark' : 'light') as 'dark' | 'light', y: { formatter: (v: number) => v.toLocaleString('th-TH') } },
  }
})
</script>
