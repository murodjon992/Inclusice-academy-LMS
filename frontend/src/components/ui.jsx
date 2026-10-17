import React, { useEffect, useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/auth'

export function Spinner() {
  return <div className="app-spinner" role="status" aria-label="Yuklanmoqda"><span></span></div>
}

// useApi natijasi uchun: yuklanayotgan / xato holatlari
export function Async({ state, children }) {
  if (state.loading) return <Spinner />
  if (state.error) {
    const notFound = state.error.status === 404
    return (
      <div className="container py-5 my-5 text-center">
        <h2 className="text-siyoh">{notFound ? 'Sahifa topilmadi' : 'Xatolik yuz berdi'}</h2>
        <p className="text-muted">{notFound ? "Siz izlagan sahifa mavjud emas." : state.error.message}</p>
        <a href="/" className="btn bg-siyoh text-light">Bosh sahifa</a>
      </div>
    )
  }
  return children(state.data)
}

export function RequireAuth({ children }) {
  const { user, ready } = useAuth()
  const loc = useLocation()
  if (!ready) return <Spinner />
  if (!user) return <Navigate to={`/login-user/?next=${encodeURIComponent(loc.pathname)}`} replace />
  return children
}

export function NotFound() {
  return (
    <div className="container py-5 my-5 text-center">
      <h1 className="text-siyoh pt-5">404</h1>
      <h3>Sahifa topilmadi</h3>
      <a href="/" className="btn bg-siyoh text-light mt-3 mb-5">Bosh sahifaga qaytish</a>
    </div>
  )
}

// owl-carousel o'rniga: bosh sahifa banner slayderi
export function Hero({ banners }) {
  const [active, setActive] = useState(0)
  const n = banners.length
  useEffect(() => {
    if (n < 2) return undefined
    const t = setInterval(() => setActive((a) => (a + 1) % n), 5000)
    return () => clearInterval(t)
  }, [n])
  if (!n) return null
  const b = banners[Math.min(active, n - 1)]
  return (
    <div className="hero-slide site-blocks-cover mt-5">
      <div className="intro-section mt-5" style={b.image ? { backgroundImage: `url('${b.image}')` } : undefined}>
        <div className="container">
          <div className="row align-items-center">
            <div className="col-lg-12 mx-auto text-center">
              <h1>{b.title}</h1>
              <p className="mx-auto">{b.subtitle}</p>
            </div>
          </div>
        </div>
      </div>
      {n > 1 && (
        <div className="owl-dots">
          {banners.map((x, i) => (
            <button key={x.id} type="button" aria-label={`Banner ${i + 1}`} onClick={() => setActive(i)}
              className={'owl-dot' + (i === active ? ' active' : '')} style={{ background: 'none', border: 0 }}>
              <span></span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
