import React, { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, errorText } from '../lib/api'
import { useApi } from '../lib/hooks'
import { PageTitle } from './Dashboard'

function Input({ f, value, error, onChange, onFile }) {
  const cls = 'form-control' + (error ? ' is-invalid' : '')
  switch (f.type) {
    case 'textarea':
      return <textarea className={cls} rows={5} value={value} onChange={(e) => onChange(e.target.value)} />
    case 'checkbox':
      return (
        <div className="form-check form-switch">
          <input className="form-check-input" type="checkbox" id={`f_${f.name}`} checked={!!value} onChange={(e) => onChange(e.target.checked)} />
        </div>
      )
    case 'select':
      return (
        <select className={'form-select' + (error ? ' is-invalid' : '')} value={value} onChange={(e) => onChange(e.target.value)}>
          <option value="">---------</option>
          {f.choices.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      )
    case 'multiselect':
      return (
        <select multiple className={'form-select' + (error ? ' is-invalid' : '')} value={value}
          onChange={(e) => onChange(Array.from(e.target.selectedOptions, (o) => o.value))}>
          {f.choices.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
        </select>
      )
    case 'file':
    case 'image':
      return (
        <>
          {f.current && (
            <div className="mb-2">
              {f.type === 'image'
                ? <img src={f.current} alt="" style={{ maxHeight: 90, borderRadius: 4 }} />
                : <a href={f.current} target="_blank" rel="noreferrer"><i className="bi bi-file-earmark"></i> Joriy fayl</a>}
              <div className="form-text">Yangisini tanlasangiz, eskisi almashtiriladi.</div>
            </div>
          )}
          <input type="file" className={cls} accept={f.type === 'image' ? 'image/*' : undefined}
            onChange={(e) => onFile(e.target.files[0] || null)} />
        </>
      )
    default: {
      const type = { datetime: 'datetime-local' }[f.type] || f.type
      return (
        <input className={cls} type={type} value={value} maxLength={f.max_length || undefined}
          autoComplete={f.type === 'password' ? 'new-password' : undefined} onChange={(e) => onChange(e.target.value)} />
      )
    }
  }
}

export default function ResourceForm() {
  const { key, id } = useParams()
  const navigate = useNavigate()
  const state = useApi(id ? `/manage/${key}/${id}/` : `/manage/${key}/new/`)
  const d = state.data
  const [values, setValues] = useState({})
  const [files, setFiles] = useState({})
  const [errors, setErrors] = useState({})
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    if (!d) return
    setValues(Object.fromEntries(d.fields.map((f) => [f.name, f.value])))
    setFiles({})
    setErrors({})
  }, [d])

  if (state.error) {
    return <div className="alert alert-danger">{state.error.status === 404 ? 'Topilmadi' : state.error.message}</div>
  }
  if (state.loading || !d) return <div className="spinner-border text-primary" role="status"></div>

  const visible = (f) => !f.show_if || values[f.show_if[0]] === f.show_if[1]
  const set = (name) => (v) => setValues((x) => ({ ...x, [name]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setBusy(true); setErrors({})
    const fd = new FormData()
    d.fields.filter(visible).forEach((f) => {
      const v = values[f.name]
      if (f.type === 'file' || f.type === 'image') { if (files[f.name]) fd.append(f.name, files[f.name]) }
      else if (f.type === 'checkbox') { if (v) fd.append(f.name, 'on') }
      else if (f.type === 'multiselect') (v || []).forEach((x) => fd.append(f.name, x))
      else fd.append(f.name, v == null ? '' : v)
    })
    try {
      await api(id ? `/manage/${key}/${id}/` : `/manage/${key}/`, { method: id ? 'PUT' : 'POST', body: fd })
      navigate(`/manage-admin/r/${key}`)
    } catch (err) {
      setErrors((err.data && err.data.errors) || { non_field: [errorText(err)] })
      setBusy(false)
      window.scrollTo(0, 0)
    }
  }

  const title = id ? `${d.title}: tahrirlash` : `${d.title}: qo'shish`
  return (
    <>
      <PageTitle title={title} />
      <section className="section">
        <div className="card">
          <div className="card-body pt-4">
            <form onSubmit={submit} style={{ maxWidth: 760 }}>
              {errors.non_field && <div className="alert alert-danger">{errors.non_field.join(' ')}</div>}
              {d.fields.filter(visible).map((f) => (
                <div className="mb-3" key={f.name}>
                  <label className="form-label fw-semibold" htmlFor={`f_${f.name}`}>
                    {f.label}{f.required && f.type !== 'checkbox' ? ' *' : ''}
                  </label>
                  <Input f={f} value={values[f.name] ?? ''} error={errors[f.name]}
                    onChange={set(f.name)} onFile={(file) => setFiles((x) => ({ ...x, [f.name]: file }))} />
                  {f.help && <div className="form-text">{f.help}</div>}
                  {errors[f.name] && <div className="text-danger small mt-1">{errors[f.name].join(' ')}</div>}
                </div>
              ))}
              <button type="submit" className="btn btn-primary me-2" disabled={busy}>Saqlash</button>
              <Link to={`/manage-admin/r/${key}`} className="btn btn-outline-secondary">Bekor qilish</Link>
            </form>
          </div>
        </div>
      </section>
    </>
  )
}
