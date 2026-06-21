<script setup lang="ts">
type Color = 'indigo' | 'violet' | 'emerald'

withDefaults(
  defineProps<{ label: string; value: string; unit: string; color?: Color; subValue?: string }>(),
  { color: 'indigo' },
)

const colorMap: Record<Color, { dot: string; ring: string; ring2: string; icon: string }> = {
  indigo:  { dot: 'bg-indigo-500',  ring: 'bg-indigo-500/10',  ring2: 'bg-indigo-500/20',  icon: 'bg-indigo-600 shadow-indigo-200/50'  },
  violet:  { dot: 'bg-violet-500',  ring: 'bg-violet-500/10',  ring2: 'bg-violet-500/20',  icon: 'bg-violet-500 shadow-violet-200/50'  },
  emerald: { dot: 'bg-emerald-500', ring: 'bg-emerald-500/10', ring2: 'bg-emerald-500/20', icon: 'bg-emerald-500 shadow-emerald-200/50' },
}
</script>

<template>
  <div class="relative bg-surface rounded-xl border border-border shadow-sm p-5 overflow-hidden flex flex-col transition-all duration-300 hover:shadow-md hover:-translate-y-0.5">
    <div class="absolute -top-6 -right-6 w-28 h-28 rounded-full opacity-60 pointer-events-none" :class="colorMap[color].ring" />
    <div class="absolute -bottom-4 -right-2 w-16 h-16 rounded-full opacity-40 pointer-events-none" :class="colorMap[color].ring2" />

    <div class="relative flex-1 flex flex-col justify-center">
      <div class="flex items-start justify-between gap-3">
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-1.5 mb-3">
            <span class="w-1.5 h-1.5 rounded-full inline-block" :class="colorMap[color].dot" />
            <span class="text-[11px] font-semibold text-muted uppercase tracking-widest">{{ label }}</span>
          </div>
          <p class="text-2xl font-extrabold text-fg tabular-nums leading-tight overflow-hidden text-ellipsis whitespace-nowrap">{{ value }}</p>
          <p class="text-xs text-muted mt-1.5">{{ unit }}</p>
          <p v-if="subValue" class="text-xs text-muted font-medium mt-2 tabular-nums truncate">{{ subValue }}</p>
        </div>
        <div class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 shadow-md" :class="colorMap[color].icon">
          <slot name="icon" />
        </div>
      </div>
    </div>
  </div>
</template>
