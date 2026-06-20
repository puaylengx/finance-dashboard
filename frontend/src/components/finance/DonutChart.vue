<template>
  <div class="rounded-xl border border-[#2e3250] bg-[#1a1d27] p-5">
    <div class="text-sm font-medium text-[#8892b0] mb-4">{{ title }}</div>
    <vue-apex-charts
      type="donut" height="260"
      :options="chartOptions" :series="values"
    />
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import VueApexCharts from 'vue3-apexcharts'

const props = defineProps<{ labels: string[]; values: number[]; title?: string }>()

const COLORS = ['#6c8efb','#a78bfa','#34d399','#fbbf24','#f87171','#60a5fa','#f472b6','#4ade80']

const chartOptions = computed(() => ({
  chart:   { background: 'transparent', fontFamily: 'inherit' },
  theme:   { mode: 'dark' as const },
  labels:  props.labels.slice(0, 8),
  colors:  COLORS,
  legend:  { position: 'bottom' as const, labels: { colors: '#8892b0' } },
  dataLabels: { enabled: false },
  tooltip: { theme: 'dark' as const, y: { formatter: (v: number) => v.toLocaleString('th-TH') } },
  plotOptions: { pie: { donut: { size: '60%' } } },
}))
</script>
