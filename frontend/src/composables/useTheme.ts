import { ref, watchEffect } from 'vue'

type Theme = 'dark' | 'light'

const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'dark')

watchEffect(() => {
  document.documentElement.setAttribute('data-theme', theme.value)
  localStorage.setItem('theme', theme.value)
})

export function useTheme() {
  const toggle = () => { theme.value = theme.value === 'dark' ? 'light' : 'dark' }
  const isDark = () => theme.value === 'dark'
  return { theme, toggle, isDark }
}
