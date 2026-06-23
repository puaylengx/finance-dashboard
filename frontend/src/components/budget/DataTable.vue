<template>
  <div class="rounded-xl border border-border bg-surface overflow-hidden">
    <div class="flex items-center justify-between px-5 py-4 border-b border-border">
      <div class="text-sm font-medium text-muted">{{ title }}</div>
      <button @click="$emit('export')" class="text-xs text-accent hover:underline">Export CSV</button>
    </div>
    <div v-if="!rows.length">
      <EmptyState :variant="emptyVariant" />
    </div>
    <div v-else ref="scrollRef" class="overflow-auto" style="max-height: 480px">
      <table class="w-full text-sm">
        <thead class="sticky top-0 bg-surface z-10">
          <tr class="text-muted text-left">
            <th v-for="col in columns" :key="col.key" class="px-4 py-3 font-medium">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="paddingTop > 0">
            <td :colspan="columns.length" :style="{ height: `${paddingTop}px`, padding: 0 }" />
          </tr>
          <tr
            v-for="vRow in virtualItems"
            :key="vRow.index"
            class="border-t border-border hover:bg-surface2 transition-colors"
          >
            <td v-for="col in columns" :key="col.key" class="px-4 py-3" :class="col.class">
              {{ col.format ? col.format(rows[vRow.index][col.key]) : rows[vRow.index][col.key] }}
            </td>
          </tr>
          <tr v-if="paddingBottom > 0">
            <td :colspan="columns.length" :style="{ height: `${paddingBottom}px`, padding: 0 }" />
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useVirtualizer } from '@tanstack/vue-virtual'
import EmptyState from '@/components/atoms/EmptyState.vue'

interface Column { key: string; label: string; class?: string; format?: (v: unknown) => string }
const props = defineProps<{
  title?: string
  columns: Column[]
  rows: Record<string, unknown>[]
  emptyVariant?: 'no-data' | 'no-results' | 'no-permission'
}>()
defineEmits<{ (e: 'export'): void }>()

const scrollRef = ref<HTMLElement | null>(null)

const rowVirtualizer = useVirtualizer(
  computed(() => ({
    count: props.rows.length,
    getScrollElement: () => scrollRef.value,
    estimateSize: () => 44,
    overscan: 5,
  }))
)

const virtualItems = computed(() => rowVirtualizer.value.getVirtualItems())

const paddingTop = computed(() => virtualItems.value[0]?.start ?? 0)
const paddingBottom = computed(() => {
  const last = virtualItems.value.at(-1)
  return last ? rowVirtualizer.value.getTotalSize() - last.end : 0
})
</script>
