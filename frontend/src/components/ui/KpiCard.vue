<template>
  <div class="rounded-xl border border-border bg-surface p-5 flex flex-col gap-2">
    <div class="text-sm text-muted">{{ label }}</div>
    <div class="text-2xl font-semibold tracking-tight" :class="valueClass">{{ formatted }}</div>
    <div v-if="sub" class="text-xs text-muted">{{ sub }}</div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { fmt } from '@/utils/format'

const props = withDefaults(defineProps<{
  label: string; value: number; sub?: string; color?: string; prefix?: string; suffix?: string
}>(), { color: 'text-fg' })

const formatted  = computed(() => `${props.prefix ?? ''}${fmt(props.value)}${props.suffix ?? ''}`)
const valueClass = computed(() => props.color)
</script>
