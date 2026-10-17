import React from 'react'

const MONTHS_SHORT = ['yan', 'fev', 'mar', 'apr', 'may', 'iyn', 'iyl', 'avg', 'sen', 'okt', 'noy', 'dek']
const MONTHS_LONG = ['yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun', 'iyul', 'avgust', 'sentabr', 'oktabr', 'noyabr', 'dekabr']
const pad = (n) => String(n).padStart(2, '0')

// Django date filtri formatlarining kerakli qismi: d, m, M, F, Y, H, i
export function fmtDate(value, format = 'd.m.Y') {
  if (!value) return ''
  const d = new Date(value)
  if (isNaN(d)) return ''
  const map = {
    d: pad(d.getDate()), m: pad(d.getMonth() + 1), M: MONTHS_SHORT[d.getMonth()],
    F: MONTHS_LONG[d.getMonth()], Y: String(d.getFullYear()), H: pad(d.getHours()), i: pad(d.getMinutes()),
  }
  return String(format).replace(/[dmMFYHi]/g, (c) => map[c])
}

export function truncate(value, n) {
  const s = value == null ? '' : String(value)
  return s.length > n ? s.slice(0, Math.max(n - 1, 0)) + '…' : s
}

// Django "linebreaks" filtri: bo'sh qator -> <p>, bitta qator -> <br>
export function Linebreaks({ text }) {
  if (!text) return null
  return text.split(/\n{2,}/).map((para, i) => (
    <p key={i}>
      {para.split('\n').map((line, j, arr) => (
        <React.Fragment key={j}>{line}{j < arr.length - 1 && <br />}</React.Fragment>
      ))}
    </p>
  ))
}
