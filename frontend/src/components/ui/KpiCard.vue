<template>
  <div class="rounded-xl border border-[#2e3250] bg-[#1a1d27] p-5 flex flex-col gap-2">
    <div class="text-sm text-[#8892b0]">{{ label }}</div>
    <div class="text-2xl font-semibold tracking-tight" :class="valueClass">{{ formatted }}</div>
    <div v-if="sub" class="text-xs text-[#8892b0]">{{ sub }}</div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { fmt } from '@/utils/format'

const props = withDefaults(defineProps<{
  label: string; value: number; sub?: string; color?: string; prefix?: string; suffix?: string
}>(), { color: 'text-[#e2e8f0]' })

const formatted  = computed(() => `${props.prefix ?? ''}${fmt(props.value)}${props.suffix ?? ''}`)
const valueClass = computed(() => props.color)
</script>
