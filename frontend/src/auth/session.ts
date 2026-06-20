export interface AuthUser {
  name: string; username: string; role: string
  position: string | null; coordinator: boolean
  token: string; expiresAt: number
}

const KEY = 'auth_user'

export function saveSession(user: AuthUser): void {
  sessionStorage.setItem(KEY, JSON.stringify(user))
}

export function getSession(): AuthUser | null {
  const raw = sessionStorage.getItem(KEY)
  if (!raw) return null
  try {
    const data: AuthUser = JSON.parse(raw)
    if (Date.now() > data.expiresAt) { clearSession(); return null }
    return data
  } catch { clearSession(); return null }
}

export const getToken      = (): string | null => getSession()?.token ?? null
export const clearSession  = (): void => sessionStorage.removeItem(KEY)
export const msUntilExpiry = (): number => Math.max(0, (getSession()?.expiresAt ?? 0) - Date.now())
