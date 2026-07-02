import { createApp }    from 'vue'
import { createPinia }  from 'pinia'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { BrowserUtils } from '@azure/msal-browser'
import { broadcastResponseToMainFrame } from '@azure/msal-browser/redirect-bridge'
import router           from '@/router'
import App              from './App.vue'
import './style.css'
import { msalInstance, isMsalConfigured } from '@/lib/msalConfig'

// redirectUri ชี้กลับมาที่หน้าหลักนี้เอง (window.location.origin)
// ถ้าหน้านี้คือ popup ที่ Microsoft ส่ง auth response กลับมา ให้ broadcast กลับไปหน้าหลัก
// แล้วปิด popup ทันที โดยไม่ mount แอปเต็มรูปแบบขึ้นมาซ้ำ
if (BrowserUtils.isInPopup()) {
  broadcastResponseToMainFrame().catch((err) => {
    console.error('Failed to process auth redirect response:', err)
  })
} else {
  if (isMsalConfigured()) {
    await msalInstance.initialize()
  }

  const queryClient = new QueryClient({
    defaultOptions: { queries: { staleTime: 5 * 60_000, retry: 1 } },
  })

  createApp(App)
    .use(createPinia())
    .use(router)
    .use(VueQueryPlugin, { queryClient })
    .mount('#app')
}
