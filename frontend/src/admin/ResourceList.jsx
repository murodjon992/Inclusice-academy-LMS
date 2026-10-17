import React, { useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import { fmtDate } from '../lib/helpers'
import { useApi } from '../lib/hooks'
import { PageTitle } from './Dashboard'

function Cell({ kind, value }) {
  if (value === null || value === undefined || value === '') return <span className="text-muted">—</span>
  switch (kind) {
    case 'image': return <img src={value} alt="" style={{ height: 60, maxWidth: 120, objectFit: 'cover', borderRadius: 4 }} />
    case 'file': return <a href={value} target="_blank" rel="noreferrer"><i className="bi bi-file-earmark"></i> Fayl</a>
    case 'video': return <video src={value} controls preload="none" style={{ width: 180, height: 100 }} />
    case 'youtube': return <iframe src={value} title="youtube" loading="lazy" style={{ width: 180, height: 100, border: 0 }} allowFullScreen />
    case 'media':
      if (value.embed_url) return <iframe src={value.embed_url} title="video" loading="lazy" style={{ width: 180, height: 100, border: 0 }} allowFullScreen />
      if (value.file) return <video src={value.file} controls preload="none" style={{ width: 180, height: 100 }} />
      return <span className="text-muted">—</span>
    case 'bool': return value ? <span className="badge bg-success">Ha</span> : <span className="badge bg-secondary">Yo'q</span>
    case 'date': return fmtDate(value, 'd.m.Y')
    case 'datetime': return fmtDate(value, 'd.m.Y H:i')
    default: return String(value)
  }
}

export function Pager({ page, pages, onPage }) {
  if (pages <= 1) return null
  return (
    <nav className="mt-3"><ul className="pagination mb-0">
      <li className={'page-item' + (page <= 1 ? ' disabled' : '')}><button className="page-link" onClick={() => onPage(page - 1)}>&laquo;</button></li>
      <li className="page-item disabled"><span className="page-link">{page} / {pages}</span></li>
      <li className={'page-item' + (page >= pages ? ' disabled' : '')}><button className="page-link" onClick={() => onPage(page + 1)}>&raquo;</button></li>
    </ul></nav>
  )
}

export default function ResourceList() {
  const { key } = useParams()
  const [params, setParams] = useSearchParams()
  const page = Number(params.get('page') || 1)
  const q = params.get('q') || ''
  const [term, setTerm] = useState(q)
  const [error, setError] = useState('')
  const state = useApi(`/manage/${key}/?page=${page}&q=${encodeURIComponent(q)}`)
  const d = state.data

  const remove = async (row) => {
    if (!window.confirm("O'chirishni tasdiqlaysizmi?")) return
    setError('')
    try {
      await api(`/manage/${key}/${row.id}/`, { method: 'DELETE' })
      state.reload()
    } catch (e) { setError(e.message) }
  }
  const go = (patch) => {
    const next = new URLSearchParams(params)
    Object.entries(patch).forEach(([k, v]) => (v ? next.set(k, v) : next.delete(k)))
    setParams(next)
  }

  if (state.error) {
    return <div className="alert alert-danger">{state.error.status === 404 ? "Bunday bo'lim yo'q" : state.error.message}</div>
  }
  return (
    <>
      <PageTitle title={d ? d.title : '...'}>
        <Link to={`/manage-admin/r/${key}/new`} className="btn btn-primary"><i className="bi bi-plus-lg"></i> Qo'shish</Link>
      </PageTitle>
      <section className="section">
        <div className="card">
          <div className="card-body pt-3">
            {d && d.searchable && (
              <form className="row g-2 mb-3" onSubmit={(e) => { e.preventDefault(); go({ q: term, page: '' }) }}>
                <div className="col-sm-6 col-md-4"><input className="form-control" placeholder="Qidirish..." value={term} onChange={(e) => setTerm(e.target.value)} /></div>
                <div className="col-auto"><button className="btn btn-outline-primary" type="submit"><i className="bi bi-search"></i></button></div>
                {q && <div className="col-auto"><button className="btn btn-link" type="button" onClick={() => { setTerm(''); go({ q: '', page: '' }) }}>Tozalash</button></div>}
              </form>
            )}
            {error && <div className="alert alert-danger">{error}</div>}
            {state.loading ? <div className="spinner-border text-primary" role="status"></div> : (
              <div className="table-responsive">
                <table className="table table-hover align-middle">
                  <thead>
                    <tr><th>#</th>{d.columns.map((c) => <th key={c.key}>{c.label}</th>)}<th style={{ width: 120 }}>Amallar</th></tr>
                  </thead>
                  <tbody>
                    {d.rows.map((r) => (
                      <tr key={r.id}>
                        <td>{r.id}</td>
                        {d.columns.map((c) => <td key={c.key}><Cell kind={c.kind} value={r[c.key]} /></td>)}
                        <td className="text-nowrap">
                          <Link to={`/manage-admin/r/${key}/${r.id}`} className="btn btn-sm btn-outline-success me-1" title="Tahrirlash"><i className="bi bi-pencil"></i></Link>
                          <button type="button" className="btn btn-sm btn-outline-danger" title="O'chirish" onClick={() => remove(r)}><i className="bi bi-trash"></i></button>
                        </td>
                      </tr>
                    ))}
                    {!d.rows.length && <tr><td colSpan={d.columns.length + 2} className="text-center text-muted py-4">Ma'lumot yo'q</td></tr>}
                  </tbody>
                </table>
              </div>
            )}
            {d && <div className="d-flex justify-content-between align-items-center">
              <Pager page={d.page} pages={d.pages} onPage={(p) => go({ page: String(p) })} />
              <small className="text-muted">Jami: {d.count}</small>
            </div>}
          </div>
        </div>
      </section>
    </>
  )
}
