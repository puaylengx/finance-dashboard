<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import type { ApexOptions } from 'apexcharts'
import { fmt, fmtShort, niceScale } from '@/utils/format'
import { useTheme } from '@/composables/useTheme'

interface TrendItem {
  month: string; month_number: number; fiscal_month: number
  pa_month?: number; total: number
}

const props = withDefaults(
  defineProps<{ trendData: TrendItem[]; yearType?: 'fiscal' | 'pa' }>(),
  { trendData: () => [], yearType: 'fiscal' },
)

const { theme } = useTheme()

const Q_COLORS = ['#2563eb', '#6366f1', '#8b5cf6', '#06b6d4']

const Q_LABELS = computed(() =>
  props.yearType === 'pa'
    ? ['Q1 (Jul–Sep)', 'Q2 (Oct–Dec)', 'Q3 (Jan–Mar)', 'Q4 (Apr–Jun)']
    : ['Q1 (Oct–Dec)', 'Q2 (Jan–Mar)', 'Q3 (Apr–Jun)', 'Q4 (Jul–Sep)'],
)

const quarters = computed(() => {
  const q = [0, 0, 0, 0]
  for (const item of props.trendData) {
    const m = props.yearType === 'pa' ? (item.pa_month ?? item.fiscal_month) : item.fiscal_month
    q[Math.floor((m - 1) / 3)] += item.total
  }
  return q
})

const series = computed(() => [{ name: 'Amount', data: quarters.value }])
const chartVersion = ref(0)
watch([quarters, () => props.yearType], () => { chartVersion.value++ })

const options = computed((): ApexOptions => {
  const dark = theme.value === 'dark'
  const { min: xMin, max: xMax, tickAmount } = niceScale(Math.max(...quarters.value, 1), 0, 5)
  return {
    chart: { toolbar: { show: false }, background: 'transparent' },
    theme: { mode: dark ? 'dark' : 'light' },
    colors: Q_COLORS,
    plotOptions: {
      bar: {
        horizontal: true,
        borderRadius: 6,
        distributed: true,
        dataLabels: { position: 'top' },
      },
    },
    dataLabels: {
      enabled: true,
      textAnchor: 'start' as const,
      formatter: (v: number) => fmtShort(v),
      style: { fontSize: '11px', fontWeight: 'bold', colors: [dark ? '#e2e8f0' : '#1f2937'] },
      offsetX: 8,
    },
    legend: { show: false },
    xaxis: {
      categories: Q_LABELS.value,
      min: xMin,
      max: xMax,
      tickAmount,
      labels: {
        formatter: (v: string) => {
          const n = Number(v)
          if (n >= 1_000_000) return (n / 1_000_000).toFixed(0) + 'M'
          if (n >= 1_000)     return (n / 1_000).toFixed(0) + 'K'
          return v
        },
        style: { colors: dark ? '#8892b0' : '#4b5563', fontSize: '11px' },
      },
      axisBorder: { show: false },
    },
    yaxis: {
      labels: { style: { colors: dark ? '#8892b0' : '#374151', fontSize: '12px', fontWeight: '500' } },
    },
    grid: {
      borderColor: dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)',
      xaxis: { lines: { show: true } },
      yaxis: { lines: { show: false } },
      padding: { left: 0, right: 0, top: 0, bottom: 0 },
    },
    tooltip: {
      theme: dark ? 'dark' : 'light',
      y: { formatter: (v: number) => fmt(v) + ' THB' },
    },
  }
})
</script>

<template>
  <div class="bg-surface rounded-xl border border-border shadow-sm p-5 flex flex-col flex-1">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4 shrink-0">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-indigo-500/10 flex items-center justify-center shrink-0">
          <svg class="w-3.5 h-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
        <h2 class="text-sm font-semibold text-fg">Quarterly Spending</h2>
      </div>
      <span class="text-[10px] text-muted font-medium">Amount (THB)</span>
    </div>

    <!-- Legend -->
    <div class="flex flex-wrap gap-x-4 gap-y-1.5 mb-3 shrink-0">
      <div v-for="(q, i) in Q_LABELS" :key="i" class="flex items-center gap-1.5">
        <span class="w-2.5 h-2.5 rounded-full shrink-0" :style="{ backgroundColor: Q_COLORS[i] }"></span>
        <span class="text-[11px] text-muted">{{ q }}</span>
      </div>
    </div>

    <div v-if="!trendData.length" class="flex-1 flex items-center justify-center text-muted text-sm">No data</div>
    <div v-else class="flex-1">
      <VueApexCharts type="bar" height="220" :key="chartVersion" :options="options" :series="series" />
    </div>
  </div>
</template>
