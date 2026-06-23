import { reactive } from 'vue'

interface Toast {
  id: number
  message: string
  type: 'error' | 'success' | 'info'
}

let _seq = 0
const toasts = reactive<Toast[]>([])

export function useToast() {
  function show(message: string, type: Toast['type'] = 'info', durationMs = 4000) {
    const id = ++_seq
    toasts.push({ id, message, type })
    setTimeout(() => dismiss(id), durationMs)
  }

  function dismiss(id: number) {
    const idx = toasts.findIndex(t => t.id === id)
    if (idx !== -1) toasts.splice(idx, 1)
  }

  return {
    toasts,
    error: (msg: string) => show(msg, 'error'),
    success: (msg: string) => show(msg, 'success'),
    info: (msg: string) => show(msg, 'info'),
    dismiss,
  }
}
