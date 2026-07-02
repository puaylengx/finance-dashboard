/// <reference types="vitest/config" />
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
      headers: {
        'Content-Security-Policy': [
          "default-src 'self'",
          "script-src 'self'",
          "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
          "font-src 'self' https://fonts.gstatic.com",
          "img-src 'self' data: blob:",
          `connect-src 'self' ws://localhost:5173 ${backendUrl} https://login.microsoftonline.com`,
          "frame-ancestors 'none'",
          "base-uri 'self'",
          "form-action 'self'",
        ].join('; '),
      },
    },
    build: {
      rollupOptions: {
        input: {
          main: resolve(__dirname, 'index.html'),
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
    test: {
      environment: 'jsdom',
      include: ['src/**/*.test.ts', 'src/**/*.spec.ts'],
    },
  }
})
