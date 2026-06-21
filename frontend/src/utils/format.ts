export const fmt = (n: number | null | undefined): string => {
  if (n == null) return '-'
  return n.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

export const fmtRound = (n: number | null | undefined): string => {
  if (n == null) return '-'
  return Math.round(n).toLocaleString('th-TH')
}

export const fmtShort = (n: number | null | undefined): string => {
  if (n == null) return '-'
  const v = Number(n)
  if (v >= 1_000_000_000) return `${(v / 1_000_000_000).toFixed(1)}B`
  if (v >= 1_000_000)     return `${(v / 1_000_000).toFixed(1)}M`
  if (v >= 1_000)         return `${(v / 1_000).toFixed(1)}K`
  return String(v)
}

export const fmtPct = (n: number): string => `${n.toFixed(1)}%`

const FISCAL_MONTHS_TH = ['ต.ค.','พ.ย.','ธ.ค.','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.']
export const fiscalMonthName = (m: number): string => FISCAL_MONTHS_TH[(m - 1) % 12] ?? ''

export function niceScale(
  rawMax: number,
  rawMin = 0,
  targetTicks = 6,
): { min: number; max: number; tickAmount: number } {
  if (rawMax <= 0) return { min: 0, max: 5, tickAmount: 1 }
  const unit = rawMax >= 1_000_000_000 ? 1_000_000_000
             : rawMax >= 1_000_000     ? 1_000_000
             : rawMax >= 1_000         ? 1_000
             : 1
  const maxU  = rawMax / unit
  const minU  = Math.max(0, rawMin / unit)
  const rough = (maxU - minU) / targetTicks
  let step: number
  if (rough <= 0) {
    step = 5
  } else {
    const r    = rough / 5
    const mag  = Math.pow(10, Math.floor(Math.log10(r)))
    const norm = r / mag
    const nice = norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 5 ? 5 : 10
    step = Math.max(5, nice * mag * 5)
  }
  const niceMax = Math.ceil(maxU / step) * step
  const niceMin = Math.max(0, Math.floor(minU / step) * step)
  return {
    min:        niceMin * unit,
    max:        niceMax * unit,
    tickAmount: Math.round((niceMax - niceMin) / step),
  }
}
