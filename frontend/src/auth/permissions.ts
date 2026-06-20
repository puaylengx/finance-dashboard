export const FA_ROLES       = new Set(['fa'])
export const DIVISION_ROLES = new Set(['bba', 'hld', 'sci', 'ss', 'thm', 'faa', 'mba', 'mm'])
export const POSITION_ROLES = new Set(['chief', 'chairman', 'head'])

export const PAGE_ROLES: Record<string, Set<string> | null> = {
  finance: new Set(['fa']),
  budget:  null,
  io:      null,
}

export function extractClaims(jobTitle: string): { role: string; position: string | null } {
  const parts = jobTitle.split(',').map(p => p.trim().toLowerCase()).filter(Boolean)
  if (!parts.length) return { role: 'user', position: null }
  if (POSITION_ROLES.has(parts.at(-1)!))
    return { position: parts.at(-1)!, role: parts.length >= 2 ? parts.at(-2)! : 'user' }
  return { role: parts.at(-1)!, position: null }
}

export const isFA        = (role: string)                     => FA_ROLES.has(role.toLowerCase())
export const isDivision  = (role: string)                     => DIVISION_ROLES.has(role.toLowerCase())
export const hasPosition = (pos: string | null | undefined)   => !!pos && POSITION_ROLES.has(pos.toLowerCase())
export const canAccess   = (role: string, page: string)       => {
  const allowed = PAGE_ROLES[page]
  return allowed === null || allowed.has(role.toLowerCase())
}
