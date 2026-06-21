<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import VueApexCharts from 'vue3-apexcharts'
import type { ApexOptions } from 'apexcharts'
import { fmt } from '@/utils/format'
import { useTheme } from '@/composables/useTheme'

interface GlRow { gl_id: string; gl_description: string; gl_group: string; total: number }

const props = withDefaults(
  defineProps<{ rows: GlRow[]; chartColors?: string[] }>(),
  {
    rows: () => [],
    chartColors: () => [
      '#2563eb','#ec4899','#ca8a04','#10b981','#8b5cf6',
      '#14b8a6','#06b6d4','#6366f1','#f97316','#64748b',
    ],
  },
)

const { theme } = useTheme()

const grouped = computed(() => {
  const map = new Map<string, number>()
  for (const row of props.rows)
    map.set(row.gl_group, (map.get(row.gl_group) ?? 0) + row.total)
  return [...map.entries()].sort((a, b) => b[1] - a[1])
})

const total = computed(() => grouped.value.reduce((s, [, v]) => s + v, 0))

const chartVersion = ref(0)
watch([() => props.rows, () => props.chartColors, theme], () => { chartVersion.value++ }, { deep: true })

const series = computed(() => grouped.value.map(([, v]) => v))
const labels = computed(() => grouped.value.map(([g]) => g))

const options = computed((): ApexOptions => {
  const dark = theme.value === 'dark'
  return {
    chart: { toolbar: { show: false }, background: 'transparent' },
    theme: { mode: dark ? 'dark' : 'light' },
    colors: grouped.value.map((_, i) => props.chartColors[i % props.chartColors.length]),
    labels: labels.value,
    legend: {
      position: 'right',
      fontSize: '11px',
      labels: { colors: dark ? '#8892b0' : '#374151' },
      itemMargin: { vertical: 2 },
    },
    plotOptions: {
      pie: {
        donut: {
          size: '60%',
          labels: {
            show: true,
            value: {
              show: true,
              fontSize: '14px',
              fontWeight: '700',
              color: dark ? '#e2e8f0' : '#111827',
              formatter: (val: string) => {
                const pct = total.value > 0 ? ((Number(val) / total.value) * 100).toFixed(1) : '0.0'
                return `${fmt(Number(val))} (${pct}%)`
              },
            },
            total: {
              show: true,
              label: 'Total',
              fontSize: '11px',
              color: dark ? '#8892b0' : '#6b7280',
              formatter: () => fmt(total.value),
            },
          },
        },
      },
    },
    dataLabels: {
      enabled: true,
      formatter: (val: number) => (val < 3 ? '' : val.toFixed(1) + '%'),
      style: { fontSize: '11px', fontWeight: 'bold', colors: ['#ffffff'] },
      dropShadow: { enabled: true, top: 1, left: 1, blur: 3, color: '#000', opacity: 0.65 },
    },
    tooltip: {
      theme: dark ? 'dark' : 'light',
      y: {
        formatter: (v: number) => {
          const pct = total.value > 0 ? ((v / total.value) * 100).toFixed(1) : '0.0'
          return `${fmt(v)} THB (${pct}%)`
        },
      },
    },
    stroke: { width: 2, colors: [dark ? '#1a1d27' : '#ffffff'] },
    states: {
      hover:  { filter: { type: 'darken' as const } },
      active: { filter: { type: 'darken' as const } },
    },
  }
})
</script>

<template>
  <div class="bg-surface rounded-xl border border-border shadow-sm p-5">
    <div class="flex items-center gap-2 mb-4">
      <div class="w-7 h-7 rounded-lg bg-violet-500/10 flex items-center justify-center shrink-0">
        <svg class="w-3.5 h-3.5 text-violet-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z"/>
          <path stroke-linecap="round" stroke-linejoin="round" d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z"/>
        </svg>
      </div>
      <h2 class="text-sm font-semibold text-fg">Spending by GL Group</h2>
    </div>
    <div v-if="!rows.length" class="text-center text-muted py-6 text-sm">No data</div>
    <div v-else>
      <VueApexCharts type="donut" height="288" :key="chartVersion" :options="options" :series="series" />
    </div>
  </div>
</template>
