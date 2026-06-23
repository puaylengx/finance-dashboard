import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const backendUrl = env.VITE_API_BASE_URL || 'http://localhost:8000'

  return {
    plugins: [vue(), tailwindcss()],
    resolve: {
      alias: { '@': resolve(__dirname, 'src') },
    },
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
        },
      },
    },
    build: {
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html'),
          authRedirect: resolve(__dirname, 'auth-redirect.html'),
        },
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
  }
})
