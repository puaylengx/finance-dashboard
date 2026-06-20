export const fmt      = (n: number)  => n.toLocaleString('th-TH', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
export const fmtShort = (n: number)  => n >= 1_000_000 ? `${(n / 1_000_000).toFixed(1)}M` : n >= 1_000 ? `${(n / 1_000).toFixed(1)}K` : String(n)
export const fmtPct   = (n: number)  => `${n.toFixed(1)}%`

const FISCAL_MONTHS = ['ต.ค.','พ.ย.','ธ.ค.','ม.ค.','ก.พ.','มี.ค.','เม.ย.','พ.ค.','มิ.ย.','ก.ค.','ส.ค.','ก.ย.']
export const fiscalMonthName = (m: number) => FISCAL_MONTHS[(m - 1) % 12] ?? ''
