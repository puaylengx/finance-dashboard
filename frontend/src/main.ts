import { createApp }    from 'vue'
import { createPinia }  from 'pinia'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import router           from '@/router'
import App              from './App.vue'
import './style.css'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 5 * 60_000, retry: 1 } },
})

createApp(App)
  .use(createPinia())
  .use(router)
  .use(VueQueryPlugin, { queryClient })
  .mount('#app')
