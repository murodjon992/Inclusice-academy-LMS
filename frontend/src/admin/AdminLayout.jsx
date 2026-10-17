import React, { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { useApi } from '../lib/hooks'

const GROUP_ICONS = {
  "Testlar bo'limi": 'bi-menu-button-wide', Kurslar: 'bi-journal-text', "O'qitish amaliyoti": 'bi-mortarboard',
  Kutubxona: 'bi-book', Videolar: 'bi-camera-video', Sayt: 'bi-newspaper', Foydalanuvchilar: 'bi-people',
}

function Group({ group, pathname }) {
  const items = group.title === 'Kurslar' ? [...group.items, { key: '__progress', title: "Kurs jarayoni (o'quvchilar)" }] : group.items
  const active = items.some((i) => pathname.startsWith(i.key === '__progress' ? '/manage-admin/progress' : `/manage-admin/r/${i.key}`))
  const [open, setOpen] = useState(active)
  useEffect(() => { if (active) setOpen(true) }, [active])
  return (
    <li className="nav-item">
      <a className={'nav-link' + (open ? '' : ' collapsed')} href="#" onClick={(e) => { e.preventDefault(); setOpen((o) => !o) }}>
        <i className={'bi ' + (GROUP_ICONS[group.title] || 'bi-circle')}></i><span>{group.title}</span>
        <i className="bi bi-chevron-down ms-auto"></i>
      </a>
      <ul className={'nav-content collapse' + (open ? ' show' : '')}>
        {items.map((i) => (
          <li key={i.key}>
            <NavLink to={i.key === '__progress' ? '/manage-admin/progress' : `/manage-admin/r/${i.key}`}
              className={({ isActive }) => (isActive ? 'active' : '')}>
              <i className="bi bi-circle"></i><span>{i.title}</span>
            </NavLink>
          </li>
        ))}
      </ul>
    </li>
  )
}

export default function AdminLayout() {
  const { user } = useAuth()
  const { pathname } = useLocation()
  const menu = useApi('/manage/menu/')
  const groups = (menu.data && menu.data.groups) || []

  const toggle = () => document.body.classList.toggle('toggle-sidebar')
  useEffect(() => { window.scrollTo(0, 0) }, [pathname])

  return (
    <>
      <header id="header" className="header fixed-top d-flex align-items-center">
        <div className="d-flex align-items-center justify-content-between">
          <Link to="/manage-admin/" className="logo d-flex align-items-center">
            <span className="d-none d-lg-block">Inclusive Admin</span>
          </Link>
          <i className="bi bi-list toggle-sidebar-btn" onClick={toggle}></i>
        </div>
        <nav className="header-nav ms-auto">
          <ul className="d-flex align-items-center">
            <li className="nav-item pe-3">
              <a className="nav-link" href="/" target="_blank" rel="noreferrer"><i className="bi bi-box-arrow-up-right me-1"></i> Saytni ko'rish</a>
            </li>
            <li className="nav-item pe-3 d-none d-md-block"><span className="text-secondary">{user.username}</span></li>
            <li className="nav-item pe-3">
              <a className="btn btn-sm btn-outline-secondary" href="/logout/"><i className="bi bi-box-arrow-right"></i> Chiqish</a>
            </li>
          </ul>
        </nav>
      </header>

      <aside id="sidebar" className="sidebar">
        <ul className="sidebar-nav" id="sidebar-nav">
          <li className="nav-item">
            <NavLink to="/manage-admin/" end className={({ isActive }) => 'nav-link' + (isActive ? '' : ' collapsed')}>
              <i className="bi bi-grid"></i><span>Dashboard</span>
            </NavLink>
          </li>
          {groups.map((g) => <Group key={g.title} group={g} pathname={pathname} />)}
        </ul>
      </aside>

      <main id="main" className="main">
        <Outlet />
      </main>
      <footer id="footer" className="footer">
        <div className="copyright">&copy; Inclusive Ta'lim</div>
      </footer>
    </>
  )
}
