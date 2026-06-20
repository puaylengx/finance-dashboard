<template>
  <div class="rounded-xl border border-border bg-surface p-5">
    <div class="text-sm font-medium text-muted mb-4">{{ title }}</div>
    <vue-apex-charts type="donut" height="260" :options="chartOptions" :series="values" />
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import { useTheme } from '@/composables/useTheme'

const props = defineProps<{ labels: string[]; values: number[]; title?: string }>()
const { theme } = useTheme()

const COLORS = ['#6c8efb','#a78bfa','#34d399','#fbbf24','#f87171','#60a5fa','#f472b6','#4ade80']

const chartOptions = computed(() => {
  const dark = theme.value === 'dark'
  return {
    chart:   { background: 'transparent', fontFamily: 'inherit' },
    theme:   { mode: (dark ? 'dark' : 'light') as 'dark' | 'light' },
    labels:  props.labels.slice(0, 8),
    colors:  COLORS,
    legend:  { position: 'bottom' as const, labels: { colors: dark ? '#8892b0' : '#64748b' } },
    dataLabels: { enabled: false },
    tooltip: { theme: (dark ? 'dark' : 'light') as 'dark' | 'light', y: { formatter: (v: number) => v.toLocaleString('th-TH') } },
    plotOptions: { pie: { donut: { size: '60%' } } },
  }
})
</script>
