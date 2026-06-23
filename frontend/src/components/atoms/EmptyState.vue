<template>
  <div class="flex flex-col items-center justify-center py-16 text-center">
    <div class="w-14 h-14 rounded-2xl flex items-center justify-center mb-5" :class="iconBg">
      <!-- no-data: document empty -->
      <svg v-if="variant === 'no-data'" class="w-7 h-7" :class="iconColor" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <!-- no-results: search empty -->
      <svg v-else-if="variant === 'no-results'" class="w-7 h-7" :class="iconColor" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"/>
      </svg>
      <!-- no-permission: lock -->
      <svg v-else class="w-7 h-7" :class="iconColor" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
      </svg>
    </div>

    <h3 class="text-sm font-semibold text-fg mb-1.5">{{ resolvedTitle }}</h3>
    <p class="text-xs text-muted max-w-xs leading-relaxed">{{ resolvedDescription }}</p>

    <div v-if="$slots.action" class="mt-5">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  variant?: 'no-data' | 'no-results' | 'no-permission'
  title?: string
  description?: string
}>(), {
  variant: 'no-data',
})

const defaults = {
  'no-data': {
    title: 'ยังไม่มีข้อมูล',
    description: 'ยังไม่มีข้อมูลในระบบสำหรับช่วงเวลานี้',
    iconBg: 'bg-muted/10',
    iconColor: 'text-muted',
  },
  'no-results': {
    title: 'ไม่พบข้อมูล',
    description: 'ไม่พบข้อมูลที่ตรงกับเงื่อนไข ลองปรับหรือล้าง filter',
    iconBg: 'bg-warning/10',
    iconColor: 'text-warning',
  },
  'no-permission': {
    title: 'ไม่มีสิทธิ์เข้าถึง',
    description: 'คุณไม่มีสิทธิ์ดูข้อมูลนี้ กรุณาติดต่อผู้ดูแลระบบ',
    iconBg: 'bg-danger/10',
    iconColor: 'text-danger',
  },
}

const resolvedTitle       = computed(() => props.title       ?? defaults[props.variant].title)
const resolvedDescription = computed(() => props.description ?? defaults[props.variant].description)
const iconBg              = computed(() => defaults[props.variant].iconBg)
const iconColor           = computed(() => defaults[props.variant].iconColor)
</script>
