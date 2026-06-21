<script setup lang="ts">
type Color = 'indigo' | 'violet' | 'emerald'

const props = withDefaults(
  defineProps<{ label: string; color?: Color; topPadding?: string }>(),
  { color: 'indigo', topPadding: 'pt-1' },
)

const colorMap: Record<Color, { text: string; bg: string; border: string; line: string }> = {
  indigo:  { text: 'text-indigo-700',  bg: 'bg-indigo-50',  border: 'border-indigo-100',  line: 'bg-indigo-100'  },
  violet:  { text: 'text-violet-700',  bg: 'bg-violet-50',  border: 'border-violet-100',  line: 'bg-violet-100'  },
  emerald: { text: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-100', line: 'bg-emerald-100' },
}

const c = colorMap[props.color]
</script>

<template>
  <div class="flex items-center gap-2" :class="topPadding">
    <span
      class="text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-widest shadow-sm border"
      :class="[c.text, c.bg, c.border]"
    >{{ label }}</span>
    <div class="flex-1 h-px" :class="c.line" />
  </div>
</template>
