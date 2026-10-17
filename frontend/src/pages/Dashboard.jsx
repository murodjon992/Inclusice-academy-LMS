import React, { useState } from 'react'
import { Async } from '../components/ui'
import { useApi } from '../lib/hooks'
import { useAuth } from '../lib/auth'
import { api, errorText } from '../lib/api'
import { fmtDate } from '../lib/helpers'

function Tabs({ user, active }) {
  const tab = (href, key, label) => (
    <a href={href} className={'btn mr-2 mb-2 ' + (active === key ? 'bg-siyoh text-light' : 'btn-outline-secondary')}>{label}</a>
  )
  return (
    <div className="mb-4">
      {tab('/user-dashboard/', 'overview', 'Kabinet')}
      {tab(`/user-edit-dashboard/${user.id}`, 'edit', 'Profilni tahrirlash')}
      {tab('/dashboard/password/', 'password', 'Parolni o‘zgartirish')}
      <a href="/logout/" className="btn btn-outline-danger mb-2">Chiqish</a>
    </div>
  )
}

function Overview({ data }) {
  const { certificates, enrollments, results, user } = data
  return (
    <>
      <h4 className="text-siyoh">{user.first_name} {user.last_name}</h4>
      <p className="text-muted">{user.user_type === 'teacher' ? 'O`qituvchi' : 'Talaba'}{user.school ? ` · ${user.school}` : ''}{user.university ? ` · ${user.university}` : ''}</p>

      <h5 className="mt-4">Kurslarim</h5>
      {enrollments.length ? (
        <table className="table table-sm">
          <thead><tr><th>Kurs</th><th>Jarayon</th><th>Yozilgan sana</th></tr></thead>
          <tbody>
            {enrollments.map((e) => (
              <tr key={e.id}>
                <td><a href={`/course-detail/${e.course_slug}/`}>{e.course_title}</a></td>
                <td>{e.progress}%</td>
                <td>{fmtDate(e.enrolled_at, 'd.m.Y')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : <p className="text-muted">Hali kursga yozilmagansiz. <a href="/courses/">Kurslarni ko'rish</a></p>}

      <h5 className="mt-4">Test natijalari</h5>
      {results.length ? (
        <table className="table table-sm">
          <thead><tr><th>Test</th><th>Natija</th><th>Holat</th><th>Sana</th></tr></thead>
          <tbody>
            {results.map((r) => (
              <tr key={r.id}>
                <td>{r.quiz_title}</td>
                <td>{r.score}%</td>
                <td>{r.passed ? <span className="badge badge-success">O‘tdi</span> : <span className="badge badge-danger">O‘tmadi</span>}</td>
                <td>{fmtDate(r.completed_at, 'd.m.Y H:i')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : <p className="text-muted">Natijalar yo'q.</p>}

      <h5 className="mt-4">Sertifikatlar</h5>
      {certificates.length ? (
        <ul className="list-group">
          {certificates.map((c) => (
            <li key={c.id} className="list-group-item d-flex justify-content-between align-items-center">
              <span>{c.course_title} <small className="text-muted">({c.score}%)</small></span>
              {c.pdf ? (
                <a className="btn btn-sm bg-siyoh text-light" href={`/certificate/${c.course_id}/`}>
                  <i className="fa fa-download"></i> Yuklab olish
                </a>
              ) : <span className="text-muted small">tayyorlanmoqda</span>}
            </li>
          ))}
        </ul>
      ) : <p className="text-muted">Sertifikatlar yo'q.</p>}
    </>
  )
}

function EditProfile({ user }) {
  const { setUser } = useAuth()
  const [form, setForm] = useState({
    first_name: user.first_name || '', last_name: user.last_name || '',
    date_of_birth: user.date_of_birth || '', user_type: user.user_type,
  })
  const [msg, setMsg] = useState(null)
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const submit = async (e) => {
    e.preventDefault(); setMsg(null)
    try {
      const d = await api('/me/profile/', { method: 'PATCH', body: { ...form, date_of_birth: form.date_of_birth || null } })
      setUser(d.user)
      setMsg({ ok: true, text: 'Saqlandi' })
    } catch (err) { setMsg({ ok: false, text: errorText(err) }) }
  }
  return (
    <form onSubmit={submit} style={{ maxWidth: 520 }}>
      {msg && <div className={'alert ' + (msg.ok ? 'alert-success' : 'alert-danger')}>{msg.text}</div>}
      <div className="form-group"><label>Ismingiz</label><input className="form-control" value={form.first_name} onChange={set('first_name')} required /></div>
      <div className="form-group"><label>Familiyangiz</label><input className="form-control" value={form.last_name} onChange={set('last_name')} required /></div>
      <div className="form-group"><label>Tug`ilgan sana</label><input type="date" className="form-control" value={form.date_of_birth} onChange={set('date_of_birth')} /></div>
      <div className="form-group"><label>Foydalanuvchi turi</label>
        <select className="form-control" value={form.user_type} onChange={set('user_type')}>
          <option value="student">Talaba</option><option value="teacher">O`qituvchi</option>
        </select>
      </div>
      <button className="btn bg-siyoh text-light" type="submit">Saqlash</button>
    </form>
  )
}

function PasswordForm() {
  const [form, setForm] = useState({ old_password: '', new_password1: '', new_password2: '' })
  const [msg, setMsg] = useState(null)
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))
  const submit = async (e) => {
    e.preventDefault(); setMsg(null)
    try {
      await api('/me/password/', { method: 'POST', body: form })
      setForm({ old_password: '', new_password1: '', new_password2: '' })
      setMsg({ ok: true, text: 'Parol o‘zgartirildi' })
    } catch (err) { setMsg({ ok: false, text: errorText(err) }) }
  }
  return (
    <form onSubmit={submit} style={{ maxWidth: 520 }}>
      {msg && <div className={'alert ' + (msg.ok ? 'alert-success' : 'alert-danger')}>{msg.text}</div>}
      <div className="form-group"><label>Eski parol</label><input type="password" className="form-control" value={form.old_password} onChange={set('old_password')} required /></div>
      <div className="form-group"><label>Yangi parol</label><input type="password" className="form-control" value={form.new_password1} onChange={set('new_password1')} required /></div>
      <div className="form-group"><label>Yangi parolni takrorlang</label><input type="password" className="form-control" value={form.new_password2} onChange={set('new_password2')} required /></div>
      <button className="btn bg-siyoh text-light" type="submit">O‘zgartirish</button>
    </form>
  )
}

export default function Dashboard({ mode = 'overview' }) {
  const state = useApi('/me/dashboard/')
  return (
    <div className="container pt-5 mt-5 mb-5">
      <h2 className="text-siyoh pt-4 mb-4">Shaxsiy kabinet</h2>
      <Async state={state}>
        {(data) => (
          <>
            <Tabs user={data.user} active={mode} />
            {mode === 'overview' && <Overview data={data} />}
            {mode === 'edit' && <EditProfile user={data.user} />}
            {mode === 'password' && <PasswordForm />}
          </>
        )}
      </Async>
    </div>
  )
}
