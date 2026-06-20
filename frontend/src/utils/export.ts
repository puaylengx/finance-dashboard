export function exportCSV(rows: Record<string, unknown>[], filename: string) {
  if (!rows.length) return
  const headers = Object.keys(rows[0])
  const csv = [headers.join(','), ...rows.map(r => headers.map(h => JSON.stringify(r[h] ?? '')).join(','))].join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
  const url  = URL.createObjectURL(blob)
  const a    = Object.assign(document.createElement('a'), { href: url, download: `${filename}.csv` })
  document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url)
}

export function exportExcel(rows: Record<string, unknown>[], filename: string) {
  import('exceljs').then(({ default: ExcelJS }) => {
    const wb = new ExcelJS.Workbook()
    const ws = wb.addWorksheet('Data')
    if (!rows.length) return
    ws.columns = Object.keys(rows[0]).map(k => ({ header: k, key: k, width: 20 }))
    rows.forEach(r => ws.addRow(r))
    ws.getRow(1).font = { bold: true }
    wb.xlsx.writeBuffer().then(buf => {
      const blob = new Blob([buf], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const url  = URL.createObjectURL(blob)
      const a    = Object.assign(document.createElement('a'), { href: url, download: `${filename}.xlsx` })
      document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url)
    })
  })
}

export const printPage = () => window.print()
