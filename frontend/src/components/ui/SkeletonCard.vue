<template>
  <div class="rounded-xl bg-surface border border-border animate-skeleton" :style="{ height: height }" />
</template>
<script setup lang="ts">
withDefaults(defineProps<{ height?: string }>(), { height: '80px' })
</script>
