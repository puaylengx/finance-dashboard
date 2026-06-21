<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import type { ApexOptions } from 'apexcharts'
import { fmt, fmtShort, niceScale } from '@/utils/format'
import { useTheme } from '@/composables/useTheme'

interface CostCenterRow { cost_center_eng: string; cost_center_description: string; total: number }

const props = withDefaults(defineProps<{
  rows:       CostCenterRow[]
  title?:     string
  barColor?:  string
  hoverColor?: string
}>(), {
  rows:       () => [],
  title:      'Top Cost Centers',
  barColor:   '#2563eb',
  hoverColor: '#1d4ed8',
})

const { theme } = useTheme()
const top = computed(() => [...props.rows].sort((a, b) => b.total - a.total).slice(0, 10))

const chartVersion = ref(0)
watch([() => props.rows, theme], () => { chartVersion.value++ }, { deep: true })

const series = computed(() => [{ name: 'Amount', data: top.value.map(r => r.total) }])

const options = computed((): ApexOptions => {
  const dark  = theme.value === 'dark'
  const maxVal = Math.max(...top.value.map(r => r.total), 1)
  const { min: yMin, max: yMax, tickAmount } = niceScale(maxVal, 0, 5)
  return {
    chart: { toolbar: { show: false }, background: 'transparent' },
    theme: { mode: dark ? 'dark' : 'light' },
    colors: [props.barColor],
    plotOptions: {
      bar: { borderRadius: 8, columnWidth: '60%', dataLabels: { position: 'top' } },
    },
    dataLabels: {
      enabled: true,
      formatter: (v: number) => fmtShort(v),
      style: { fontSize: '11px', fontWeight: 'bold', colors: [dark ? '#e2e8f0' : '#1f2937'] },
      offsetY: -20,
    },
    xaxis: {
      categories: top.value.map(r => r.cost_center_description || r.cost_center_eng),
      labels: {
        style: { colors: dark ? '#8892b0' : '#4b5563', fontSize: '10px' },
        rotate: -30,
        maxHeight: 60,
      },
      axisBorder: { show: false },
      axisTicks: { show: false },
    },
    yaxis: {
      min: yMin,
      max: yMax,
      tickAmount,
      labels: {
        formatter: (v: number) => fmtShort(v),
        style: { colors: dark ? '#8892b0' : '#6b7280', fontSize: '10px' },
      },
    },
    grid: { borderColor: dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)' },
    tooltip: {
      theme: dark ? 'dark' : 'light',
      y: { formatter: (v: number) => fmt(v) + ' THB' },
    },
  }
})
</script>

<template>
  <div class="bg-surface rounded-xl border border-border shadow-sm p-5">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-7 h-7 rounded-lg bg-indigo-500/10 flex items-center justify-center shrink-0">
        <svg class="w-3.5 h-3.5 text-indigo-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"/>
        </svg>
      </div>
      <h2 class="text-sm font-semibold text-fg">{{ title }}</h2>
    </div>
    <div v-if="!rows.length" class="text-center text-muted py-6 text-sm">No data</div>
    <div v-else class="h-72">
      <VueApexCharts type="bar" height="288" :key="chartVersion" :options="options" :series="series" />
    </div>
  </div>
</template>
