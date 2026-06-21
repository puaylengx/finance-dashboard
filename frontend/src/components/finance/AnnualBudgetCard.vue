<script setup lang="ts">
import { computed } from 'vue'
import { fmt } from '@/utils/format'

const props = defineProps<{ totalAmount: number | undefined; totalBudget: number | undefined }>()

const usedPct = computed(() => {
  if (!props.totalBudget || !props.totalAmount) return 0
  return Math.min((props.totalAmount / props.totalBudget) * 100, 100)
})

const remaining = computed(() => (props.totalBudget ?? 0) - (props.totalAmount ?? 0))

const theme = computed(() => {
  const p = usedPct.value
  if (p >= 85) return { dot: 'bg-emerald-500', ring: 'bg-emerald-500/10', ring2: 'bg-emerald-500/20', icon: 'bg-emerald-500 shadow-emerald-200/50', bar: 'bg-teal-500', text: 'text-emerald-600' }
  if (p >= 65) return { dot: 'bg-amber-500',   ring: 'bg-amber-500/10',   ring2: 'bg-amber-500/20',   icon: 'bg-amber-500 shadow-amber-200/50',   bar: 'bg-amber-400',  text: 'text-amber-500'  }
  return             { dot: 'bg-red-500',     ring: 'bg-red-500/10',     ring2: 'bg-red-500/20',     icon: 'bg-red-500 shadow-red-200/50',       bar: 'bg-red-400',    text: 'text-red-500'    }
})

const tooltipText = computed(() => {
  const p = usedPct.value.toFixed(1)
  if (usedPct.value >= 85) return `${p}% — อยู่ในเกณฑ์ดี`
  if (usedPct.value >= 65) return `${p}% — ควรเร่งใช้งบประมาณ`
  return `${p}% — ต่ำกว่าเกณฑ์ ควรตรวจสอบ`
})
</script>

<template>
  <div class="relative bg-surface rounded-xl border border-border shadow-sm p-5 overflow-hidden flex flex-col transition-all duration-300 hover:shadow-md hover:-translate-y-0.5">
    <div class="absolute -top-6 -right-6 w-28 h-28 rounded-full opacity-60 pointer-events-none" :class="theme.ring" />
    <div class="absolute -bottom-4 -right-2 w-16 h-16 rounded-full opacity-40 pointer-events-none" :class="theme.ring2" />

    <div class="relative flex flex-col flex-1">
      <div class="flex items-start justify-between gap-3 mb-4">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-1.5 mb-3">
            <span class="w-1.5 h-1.5 rounded-full inline-block" :class="theme.dot" />
            <span class="text-[11px] font-semibold text-muted uppercase tracking-widest">Annual Budget</span>
          </div>
          <p class="text-2xl font-extrabold text-fg tabular-nums leading-tight overflow-hidden text-ellipsis whitespace-nowrap">{{ fmt(totalBudget) }}</p>
          <p class="text-xs text-muted mt-1.5">Amount (THB)</p>
        </div>
        <div class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 shadow-md" :class="theme.icon">
          <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
          </svg>
        </div>
      </div>

      <div class="group relative mt-auto">
        <div class="flex justify-between text-[11px] mb-1.5">
          <span class="text-muted">ใช้ไปแล้ว <span class="font-bold" :class="theme.text">{{ usedPct.toFixed(1) }}%</span></span>
          <span class="text-muted">คงเหลือ <span class="text-fg font-semibold">{{ fmt(remaining) }}</span></span>
        </div>
        <div class="h-2 bg-border rounded-full overflow-hidden">
          <div class="h-2 rounded-full transition-all duration-700" :class="theme.bar" :style="{ width: usedPct + '%' }" />
        </div>
        <div class="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10 pointer-events-none">
          <div class="bg-gray-900 text-white text-[11px] rounded-lg px-3 py-2.5 whitespace-nowrap shadow-xl">
            {{ tooltipText }}
            <div class="mt-2 space-y-1 text-gray-300">
              <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-teal-500 inline-block"></span>85%+ — อยู่ในเกณฑ์ดี</div>
              <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-amber-400 inline-block"></span>65–84% — ควรเร่งใช้งบ</div>
              <div class="flex items-center gap-1.5"><span class="w-2 h-2 rounded-full bg-red-400 inline-block"></span>น้อยกว่า 65% — ต่ำกว่าเกณฑ์</div>
            </div>
          </div>
          <div class="w-2 h-2 bg-gray-900 rotate-45 mx-auto -mt-1"></div>
        </div>
      </div>
    </div>
  </div>
</template>
