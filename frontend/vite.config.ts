import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: { '@': resolve(__dirname, 'src') },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('vue-router') || id.includes('pinia') || id.includes('node_modules/vue/')) return 'vue-core'
          if (id.includes('@tanstack') || id.includes('axios')) return 'query'
          if (id.includes('apexcharts')) return 'charts'
          if (id.includes('exceljs') || id.includes('dayjs') || id.includes('numeral') || id.includes('@vueuse')) return 'utils'
        },
      },
    },
    chunkSizeWarningLimit: 600,
  },
})
