<script setup lang="ts">
import AnnualBudgetCard from './AnnualBudgetCard.vue'
import StatCard from './StatCard.vue'
import { fmt } from '@/utils/format'

interface Kpis { total_amount?: number; total_budget?: number }

withDefaults(defineProps<{ kpis: Kpis }>(), { kpis: () => ({}) })
</script>

<template>
  <div class="flex flex-col gap-4 flex-1">
    <AnnualBudgetCard class="flex-1" :total-amount="kpis.total_amount" :total-budget="kpis.total_budget" />
    <StatCard class="flex-1" label="Total Spending" :value="fmt(kpis.total_amount)" unit="Amount (THB)">
      <template #icon>
        <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </template>
    </StatCard>
  </div>
</template>
