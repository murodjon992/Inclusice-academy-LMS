import React, { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { errorText } from '../lib/api'

// ?next= faqat sayt ichidagi yo'lga ruxsat beradi
function safeNext(next, fallback) {
  return next && next.startsWith('/') && !next.startsWith('//') ? next : fallback
}

function Field({ label, error, children }) {
  return (
    <div className="form-group">
      <label className="mb-1">{label}</label>
      {children}
      {error && <div className="form-error">{error.join(' ')}</div>}
    </div>
  )
}

export function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [params] = useSearchParams()
  const [form, setForm] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setError('')
    try {
      const user = await login(form.username, form.password)
      const next = safeNext(params.get('next'), null)
      if (next && next.startsWith('/manage-admin')) window.location.href = next
      else if (next) navigate(next)
      else if (user.is_admin) window.location.href = '/manage-admin/'
      else navigate('/user-dashboard/')
    } catch (err) {
      setError(errorText(err)); setBusy(false)
    }
  }

  return (
    <>
      <div className="pt-5 mt-5"></div>
      <div className="pt-2 mt-2"></div>
      <h1 className="text-center text-siyoh">Kirish</h1>
      <div className="container">
        <div className="row">
          <div className="col-6 offset-3">
            <form onSubmit={submit}>
              {error && <div className="alert alert-danger">{error}</div>}
              <Field label="Login"><input className="form-control" value={form.username} onChange={set('username')} required autoFocus /></Field>
              <Field label="Parol"><input className="form-control" type="password" value={form.password} onChange={set('password')} required /></Field>
              <button className="btn bg-siyoh text-light" type="submit" disabled={busy}>Login</button>
              <a href="/register/" className="btn btn-link">Ro'yxatdan o'tish</a>
            </form>
          </div>
        </div>
      </div>
    </>
  )
}

export function Register() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    username: '', first_name: '', last_name: '', date_of_birth: '', user_type: 'student',
    university: '', school: '', password1: '', password2: '',
  })
  const [errors, setErrors] = useState({})
  const [busy, setBusy] = useState(false)
  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErrors({})
    try {
      await register({ ...form, date_of_birth: form.date_of_birth || null })
      navigate('/user-dashboard/')
    } catch (err) {
      setErrors((err.data && err.data.errors) || { __all__: [errorText(err)] })
      setBusy(false)
    }
  }
  const teacher = form.user_type === 'teacher'

  return (
    <>
      <div className="pt-5 mt-5"></div>
      <div className="pt-2 mt-2"></div>
      <h1 className="text-center">Ro'yxatdan o'tish</h1>
      <div className="container">
        <div className="row">
          <div className="col-6 offset-3">
            <form onSubmit={submit}>
              {errors.__all__ && <div className="alert alert-danger">{errors.__all__.join(' ')}</div>}
              <Field label="Login" error={errors.username}><input className="form-control" value={form.username} onChange={set('username')} required /></Field>
              <div className="row">
                <div className="col-md-6"><Field label="Ismingiz" error={errors.first_name}><input className="form-control" value={form.first_name} onChange={set('first_name')} required /></Field></div>
                <div className="col-md-6"><Field label="Familiyangiz" error={errors.last_name}><input className="form-control" value={form.last_name} onChange={set('last_name')} required /></Field></div>
              </div>
              <Field label="Tug`ilgan sana" error={errors.date_of_birth}><input className="form-control" type="date" value={form.date_of_birth} onChange={set('date_of_birth')} /></Field>
              <Field label="Foydalanuvchi turi" error={errors.user_type}>
                <select className="form-control" value={form.user_type} onChange={set('user_type')}>
                  <option value="student">Talaba</option>
                  <option value="teacher">O`qituvchi</option>
                </select>
              </Field>
              {teacher ? (
                <Field label="School" error={errors.school}><input className="form-control" value={form.school} onChange={set('school')} /></Field>
              ) : (
                <Field label="University" error={errors.university}><input className="form-control" value={form.university} onChange={set('university')} /></Field>
              )}
              <Field label="Parol" error={errors.password1}><input className="form-control" type="password" value={form.password1} onChange={set('password1')} required /></Field>
              <Field label="Parolni tasdiqlang" error={errors.password2}><input className="form-control" type="password" value={form.password2} onChange={set('password2')} required /></Field>
              <button className="btn bg-siyoh text-light" type="submit" disabled={busy}>Ro'yxatdan o'tish</button>
            </form>
          </div>
        </div>
      </div>
    </>
  )
}
