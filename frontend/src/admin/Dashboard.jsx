import React from 'react'
import { useApi } from '../lib/hooks'

export function PageTitle({ title, children }) {
  return (
    <div className="pagetitle d-flex justify-content-between align-items-center">
      <div>
        <h1>{title}</h1>
        <nav>
          <ol className="breadcrumb">
            <li className="breadcrumb-item"><a href="/manage-admin/">Dashboard</a></li>
            <li className="breadcrumb-item active">{title}</li>
          </ol>
        </nav>
      </div>
      <div>{children}</div>
    </div>
  )
}

export default function Dashboard() {
  const { data, error, loading } = useApi('/manage/dashboard/')
  return (
    <>
      <div className="pagetitle">
        <h1>Dashboard</h1>
        <nav><ol className="breadcrumb"><li className="breadcrumb-item active">Bosh sahifa</li></ol></nav>
      </div>
      <section className="section dashboard">
        {loading && <div className="spinner-border text-primary" role="status"></div>}
        {error && <div className="alert alert-danger">{error.message}</div>}
        <div className="row">
          {data && data.stats.map((s) => (
            <div className="col-xxl-4 col-md-6" key={s.key}>
              <div className="card info-card sales-card">
                <div className="card-body">
                  <h5 className="card-title">{s.label}</h5>
                  <div className="d-flex align-items-center">
                    <div className="card-icon rounded-circle d-flex align-items-center justify-content-center">
                      <i className={'bi ' + s.icon}></i>
                    </div>
                    <div className="ps-3"><h6>{s.value}</h6></div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}
