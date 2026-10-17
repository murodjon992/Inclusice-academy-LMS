// Django REST API bilan ishlash: sessiya cookie + CSRF token.
function getCookie(name) {
  const m = document.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'))
  return m ? decodeURIComponent(m[1]) : ''
}

export async function api(path, { method = 'GET', body } = {}) {
  const headers = {}
  const isForm = typeof FormData !== 'undefined' && body instanceof FormData
  if (body !== undefined && !isForm) headers['Content-Type'] = 'application/json'
  if (method !== 'GET') headers['X-CSRFToken'] = getCookie('csrftoken')
  const res = await fetch('/api' + path, {
    method,
    headers,
    credentials: 'same-origin',
    body: body === undefined ? undefined : isForm ? body : JSON.stringify(body),
  })
  let data = null
  try { data = await res.json() } catch { /* bo'sh javob */ }
  if (!res.ok) {
    const err = new Error((data && data.detail) || 'Xatolik yuz berdi')
    err.status = res.status
    err.data = data
    throw err
  }
  return data
}

// Forma xatolarini ({maydon: [xabar]}) bitta matnga aylantiradi
export function errorText(err) {
  const e = err && err.data && err.data.errors
  if (e) return Object.values(e).flat().join(' ')
  return (err && err.message) || 'Xatolik yuz berdi'
}
