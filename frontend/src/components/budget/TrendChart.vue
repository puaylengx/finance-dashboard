<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import type { ApexOptions } from 'apexcharts'
import type { TrendMonthItem } from '@/types/api'
import { fmt, fmtRound, niceScale } from '@/utils/format'
import { useTheme } from '@/composables/useTheme'

const props = withDefaults(
  defineProps<{ items: TrendMonthItem[]; title?: string; yearType?: 'fiscal' | 'pa' }>(),
  { title: 'Monthly Spending Trend', yearType: 'fiscal' },
)

const { theme } = useTheme()

const sorted = computed(() =>
  [...props.items].sort((a, b) =>
    props.yearType === 'pa'
      ? (a.pa_month ?? a.fiscal_month) - (b.pa_month ?? b.fiscal_month)
      : a.fiscal_month - b.fiscal_month,
  ),
)

const chartVersion = ref(0)
watch([() => props.items, theme], () => { chartVersion.value++ }, { deep: true })

const series = computed(() => [
  { name: 'Spending', data: sorted.value.map(d => Number(d.total.toFixed(2))) },
])

const options = computed((): ApexOptions => {
  const dark   = theme.value === 'dark'
  const vals   = sorted.value.map(d => d.total)
  const minVal = vals.length ? Math.min(...vals) : 0
  const maxVal = vals.length ? Math.max(...vals) : 0
  const { min: yMin, max: yMax, tickAmount } = niceScale(
    maxVal + 10_000_000,
    Math.max(0, minVal - 10_000_000),
    6,
  )
  return {
    chart: { toolbar: { show: false }, zoom: { enabled: false }, background: 'transparent' },
    theme: { mode: dark ? 'dark' : 'light' },
    colors: ['#2563eb'],
    dataLabels: { enabled: false },
    stroke: { curve: 'smooth', width: 3, colors: ['#2563eb'] },
    fill: { type: 'solid', opacity: 0.08 },
    markers: {
      size: 5,
      colors: ['#2563eb'],
      strokeColors: dark ? '#1a1d27' : '#ffffff',
      strokeWidth: 2,
    },
    xaxis: {
      categories: sorted.value.map(d => d.month),
      labels: { style: { colors: dark ? '#8892b0' : '#6b7280', fontSize: '11px' } },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      min: yMin,
      max: yMax,
      tickAmount,
      labels: {
        style: { colors: dark ? '#8892b0' : '#6b7280', fontSize: '11px' },
        formatter: (v: number) => fmtRound(v),
      },
    },
    grid: { borderColor: dark ? '#2e3250' : '#e5e7eb', strokeDashArray: 3 },
    tooltip: {
      theme: dark ? 'dark' : 'light',
      y: { formatter: (v: number) => fmt(v) + ' THB' },
    },
  }
})
</script>

<template>
  <div class="bg-surface rounded-xl border border-border shadow-sm p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-lg bg-indigo-500/10 flex items-center justify-center shrink-0">
          <svg class="w-3.5 h-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"/>
          </svg>
        </div>
        <h2 class="text-sm font-semibold text-fg">{{ title }}</h2>
      </div>
      <span class="text-[11px] text-muted">Amount (THB)</span>
    </div>
    <VueApexCharts type="area" height="220" :key="chartVersion" :options="options" :series="series" />
  </div>
</template>
