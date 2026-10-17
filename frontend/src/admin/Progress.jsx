import React, { useState } from 'react'
import { useApi } from '../lib/hooks'
import { PageTitle } from './Dashboard'
import { Pager } from './ResourceList'

export default function Progress() {
  const [page, setPage] = useState(1)
  const { data, loading, error } = useApi(`/manage/progress/?page=${page}`)
  return (
    <>
      <PageTitle title="Kurs jarayoni" />
      <section className="section">
        <div className="card">
          <div className="card-body pt-3">
            {error && <div className="alert alert-danger">{error.message}</div>}
            {loading ? <div className="spinner-border text-primary" role="status"></div> : (
              <div className="table-responsive">
                <table className="table table-hover align-middle">
                  <thead><tr><th>#</th><th>Foydalanuvchi</th><th>Kurs</th><th>Darslar</th><th>Jarayon</th><th>Test</th></tr></thead>
                  <tbody>
                    {data.rows.map((r, i) => (
                      <tr key={r.id}>
                        <td>{(data.page - 1) * 25 + i + 1}</td>
                        <td>{r.user}</td>
                        <td>{r.course}</td>
                        <td>{r.completed} / {r.total}</td>
                        <td style={{ minWidth: 140 }}>
                          <div className="progress" style={{ height: 8 }}><div className="progress-bar" style={{ width: `${r.progress}%` }}></div></div>
                          <small>{r.progress}%</small>
                        </td>
                        <td>{r.quiz_unlocked ? <span className="badge bg-success">Ochiq</span> : <span className="badge bg-secondary">Yopiq</span>}</td>
                      </tr>
                    ))}
                    {!data.rows.length && <tr><td colSpan="6" className="text-center text-muted py-4">Ma'lumot yo'q</td></tr>}
                  </tbody>
                </table>
              </div>
            )}
            {data && <Pager page={data.page} pages={data.pages} onPage={setPage} />}
          </div>
        </div>
      </section>
    </>
  )
}
