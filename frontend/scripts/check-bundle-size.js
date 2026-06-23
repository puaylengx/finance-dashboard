#!/usr/bin/env node
/**
 * Bundle Size Budget Check
 * รัน: npm run size (ต้อง build ก่อน)
 * Exit 0 = ผ่าน, Exit 1 = exceed limit
 */
import { readdirSync, statSync, existsSync } from 'fs'
import { resolve } from 'path'

const DIST = resolve(process.cwd(), 'dist/assets')

if (!existsSync(DIST)) {
  console.error('\n ✗ dist/assets not found — run "npm run build" first\n')
  process.exit(1)
}

// ───── limits (kB, uncompressed) ────────────────────────────────────────────
// Set to current measured size + 10-15% buffer
const CHUNK_LIMITS = [
  { pattern: /^charts-.*\.js$/,     label: 'charts       (ApexCharts)',    maxKb: 1300 },
  { pattern: /^utils-.*\.js$/,      label: 'utils        (exceljs+dayjs)', maxKb: 1050 },
  { pattern: /^msalConfig-.*\.js$/, label: 'msalConfig   (MSAL)',          maxKb:  250 },
  { pattern: /^query-.*\.js$/,      label: 'query        (TanStack+axios)', maxKb: 150 },
  { pattern: /^vue-core-.*\.js$/,   label: 'vue-core     (vue+pinia+router)', maxKb: 80 },
]
const TOTAL_JS_LIMIT_KB = 2800

// ───── helpers ───────────────────────────────────────────────────────────────
const kb = (file) => statSync(resolve(DIST, file)).size / 1024
const pad = (s, n, right = false) => right ? String(s).padStart(n) : String(s).padEnd(n)

const jsFiles = readdirSync(DIST).filter(f => f.endsWith('.js'))
const totalKb = jsFiles.reduce((sum, f) => sum + kb(f), 0)

// ───── output ────────────────────────────────────────────────────────────────
console.log('\n Bundle Size Budget\n')
console.log(` ${pad('Chunk', 42)} ${pad('Size', 10, true)} ${pad('Limit', 10, true)} ${pad('', 8, true)}`)
console.log(' ' + '─'.repeat(74))

let failed = false

for (const { pattern, label, maxKb } of CHUNK_LIMITS) {
  const matched = jsFiles.filter(f => pattern.test(f))
  if (!matched.length) {
    console.log(` ${pad(label, 42)} ${pad('(none)', 10, true)} ${pad(maxKb + ' kB', 10, true)} ${pad('SKIP', 8, true)}`)
    continue
  }
  for (const file of matched) {
    const size = kb(file)
    const ok   = size <= maxKb
    if (!ok) failed = true
    const status = ok ? '✓' : '✗ FAIL'
    console.log(` ${pad(label, 42)} ${pad(size.toFixed(1) + ' kB', 10, true)} ${pad(maxKb + ' kB', 10, true)} ${pad(status, 8, true)}`)
  }
}

const totalOk = totalKb <= TOTAL_JS_LIMIT_KB
if (!totalOk) failed = true
console.log(' ' + '─'.repeat(74))
console.log(` ${pad('TOTAL JS', 42)} ${pad(totalKb.toFixed(1) + ' kB', 10, true)} ${pad(TOTAL_JS_LIMIT_KB + ' kB', 10, true)} ${pad(totalOk ? '✓' : '✗ FAIL', 8, true)}`)
console.log()

if (failed) {
  console.error(' ✗ Bundle size budget exceeded. Check added dependencies.\n')
  process.exit(1)
} else {
  console.log(' ✓ All bundle sizes within budget.\n')
}
