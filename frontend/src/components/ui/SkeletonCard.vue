<template>
  <div class="rounded-xl bg-[#1a1d27] border border-[#2e3250] animate-skeleton" :style="{ height: height }" />
</template>
<script setup lang="ts">
withDefaults(defineProps<{ height?: string }>(), { height: '80px' })
</script>
