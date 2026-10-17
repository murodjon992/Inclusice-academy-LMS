import React, { useEffect, useLayoutEffect, useRef, useState } from 'react'
import { Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'

// Django o'zi beradigan manzillar: bularda to'liq sahifa yuklanishi kerak
const SERVER_PATHS = /^\/(admin|manage-admin|logout|certificate|kutubxona\/file|media|static|api)(\/|-|$)/

const LANGS = [
  { code: 'uz', title: "O'zbekcha", img: '/static/images/uzb.png' },
  { code: 'en', title: 'English', img: '/static/images/united-kingdom.png' },
  { code: 'ru', title: 'Русский', img: '/static/images/russia.png' },
]

// Hozircha faqat o'zbek tili; boshqa tillar uchun bayroqlar tayyor turibdi
function LanguageSwitcher() {
  const [note, setNote] = useState('')
  const pick = (l) => {
    if (l.code === 'uz') return
    setNote(`${l.title} tili tez orada qo'shiladi`)
    setTimeout(() => setNote(''), 2500)
  }
  return (
    <div className="lang-switch d-flex align-items-center position-relative">
      {LANGS.map((l) => (
        <button key={l.code} type="button" title={l.title} aria-label={l.title} onClick={() => pick(l)}
          className={'lang-btn' + (l.code === 'uz' ? ' active' : '')}>
          <img width="28" height="28" src={l.img} alt={l.title} />
        </button>
      ))}
      {note && <span className="lang-note">{note}</span>}
    </div>
  )
}

function TopBar() {
  const { user } = useAuth()
  return (
    <div className="py-2 bg-light">
      <div className="container">
        <div className="row align-items-center">
          <div className="col-lg-6 d-none d-lg-block">
            <a href="#" className="small text-siyoh mr-3"><span className="icon-question-circle-o mr-2"></span> Savolingiz bormi?</a>
            <a href="#" className="small text-siyoh mr-3"><span className="icon-phone2 mr-2"></span> 10 20 123 456</a>
            <a href="#" className="small text-siyoh mr-3"><span className="icon-envelope-o mr-2"></span> info@mydomain.com</a>
          </div>
          <div className="col-lg-2">
            <LanguageSwitcher />
          </div>
          <div className="col-lg-4 text-right">
            {user ? (
              <a href={user.is_admin ? '/manage-admin/' : '/user-dashboard/'} className="small btn bg-siyoh text-light px-4 py-2 rounded-0">Kabinet</a>
            ) : (
              <>
                <a href="/login-user/" className="text-siyoh mr-3"> <i className="fa-solid fa-arrow-right-to-bracket"></i> Kirish</a>
                <a href="/register/" className="small btn bg-siyoh text-light px-4 py-2 rounded-0"><span className="icon-users"></span> <i className="fa-solid fa-person-circle-plus"></i> Ro'yxatdan o'tish</a>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function Header() {
  const { data: turlar } = useApi('/amaliyot-turlari/')
  const wrapRef = useRef(null)
  const barRef = useRef(null)
  const [shrink, setShrink] = useState(false)
  const [stuck, setStuck] = useState(false)

  // jquery.sticky o'rniga: sarlavha o'z joyida turadi (yuqori panel ostida),
  // sahifa uning o'rnidan pastga aylantirilganda ekran tepasiga qotadi.
  useLayoutEffect(() => {
    const sync = () => {
      if (wrapRef.current && barRef.current) wrapRef.current.style.height = barRef.current.offsetHeight + 'px'
    }
    sync()
    window.addEventListener('resize', sync)
    return () => window.removeEventListener('resize', sync)
  }, [shrink])
  useEffect(() => {
    const onScroll = () => {
      setShrink(window.scrollY > 100)
      setStuck(!!wrapRef.current && wrapRef.current.getBoundingClientRect().top <= 0)
    }
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  return (
    <div ref={wrapRef} className={'sticky-wrapper' + (stuck ? ' is-sticky' : '')}>
      <header ref={barRef} className={'site-navbar py-4 site-navbar-target' + (shrink ? ' shrink' : '')} role="banner"
        style={stuck ? { position: 'fixed', top: 0, left: 0, width: '100%' } : undefined}>
        <div className="container">
          <div className="d-flex align-items-center">
            <div className="site-logo">
              <a href="/" className="d-block text-siyoh m-0 p-0">Bosh Sahifa</a>
            </div>
            <nav className="site-navigation position-relative text-right" role="navigation">
              <ul className="site-menu main-menu mr-auto d-none d-lg-block">
                <li className="has-children">
                  <a href="/" className="nav-link text-left">O'qitish amaliyoti <i className="fa-solid fa-angle-down"></i></a>
                  <ul className="dropdown">
                    {(turlar || []).map((t) => (
                      <li key={t.id}><a href={`/amaliyot/${t.slug}/`}>{t.nomi}</a></li>
                    ))}
                    <li><a href="/amaliyot-list/">Barchasi</a></li>
                  </ul>
                </li>
                <li className="has-children">
                  <a href="/" className="nav-link text-left">Kutubxona <i className="fa-solid fa-angle-down"></i> </a>
                  <ul className="dropdown">
                    <li><a href="#">Online Do'kon</a></li>
                    <li><a href="/kutubxona/">Kutubxona</a></li>
                  </ul>
                </li>
                <li><a href="#" className="nav-link text-left">Yangiliklar</a></li>
                <li><a href="/kurslar/">Kurslar</a></li>
                <li><a href="/videolar/" className="nav-link text-left">Videolar</a></li>
                <li><a href="#" className="nav-link text-left">Biz Haqimizda</a></li>
              </ul>
            </nav>
          </div>
        </div>
      </header>
    </div>
  )
}

function Footer() {
  return (
    <div className="footer mt-2">
      <div className="container">
        <div className="row">
          <div className="col-lg-3">
            <h2><a href="/" className="mb-4 text-light">Inklyuziv Ta'lim</a></h2>
            <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Beatae nemo minima qui dolor, iusto iure.</p>
            <p><a href="#">Learn More</a></p>
          </div>
          <div className="col-lg-3">
            <h3 className="footer-heading"><span>Quick Links</span></h3>
            <ul className="list-unstyled">
              <li><a className="text-light" href="#">Inklyuziv resurslar</a></li>
              <li><a className="text-light" href="#">Inklyuziv maktablar haftaligi</a></li>
              <li><a className="text-light" href="#">Bizning ta'sirimiz</a></li>
              <li><a className="text-light" href="#">Biz Haqimizda</a></li>
              <li><a className="text-light" href="#">Bog'lanish</a></li>
            </ul>
          </div>
          <div className="col-lg-3">
            <h3 className="footer-heading"><span>Biz bilan bog'lanish</span></h3>
            <ul className="list-unstyled">
              <li><a className="text-light" href="#"><i className="icon-location-arrow"></i> 100258 Andijon viloyati <br /> Buloqboshi tumani,</a></li>
              <li><a className="text-light" href="#"><i className="icon-phone"></i>+998 90 123 45 67</a></li>
              <li><a className="text-light" href="#"><i className="icon-phone"></i>+998 00 000 00 00</a></li>
              <li><a className="text-light" href="#"><i className="icon-envelope"></i>info@inclusivetalim.uz</a></li>
            </ul>
          </div>
          <div className="col-lg-3">
            <h3 className="footer-heading"><span>Ijtimoiy tarmoqlarda bog'lanish</span></h3>
            <ul className="list-unstyled">
              <li>
                <a href="#"><i className="fa-brands fa-facebook fa-2x text-light"></i></a>{' '}
                <a href="#"><i className="fa-brands fa-x-twitter fa-2x text-light"></i></a>{' '}
                <a href="#"><i className="fa-brands fa-instagram fa-2x text-light"></i></a>{' '}
                <a href="#"><i className="fa-brands fa-youtube fa-2x text-light"></i></a>{' '}
                <a href="#"><i className="fa-brands fa-linkedin fa-2x text-light"></i></a>
              </li>
            </ul>
          </div>
        </div>
        <div className="row">
          <div className="col-12"><div className="copyright"></div></div>
        </div>
      </div>
    </div>
  )
}

export default function Layout() {
  const navigate = useNavigate()
  const { pathname, hash } = useLocation()

  // Sahifa almashganda tepaga qaytish (yoki #havola ga o'tish)
  useEffect(() => {
    if (hash) {
      const el = document.getElementById(hash.slice(1))
      if (el) { el.scrollIntoView(); return }
    }
    window.scrollTo(0, 0)
  }, [pathname, hash])

  // Oddiy <a href="/..."> havolalar sahifani qayta yuklamasdan React Router orqali ochiladi
  const onClick = (e) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return
    const a = e.target.closest && e.target.closest('a[href]')
    if (!a || a.target === '_blank' || a.hasAttribute('download')) return
    const href = a.getAttribute('href')
    if (href === '#') { e.preventDefault(); return }
    if (!href || !href.startsWith('/') || href.startsWith('//') || SERVER_PATHS.test(href)) return
    e.preventDefault()
    navigate(href)
  }

  return (
    <div className="site-wrap" onClick={onClick}>
      <TopBar />
      <Header />
      <main><Outlet /></main>
      <Footer />
    </div>
  )
}
