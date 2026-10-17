import { useCallback, useEffect, useState } from 'react'
import { api } from './api'

// GET so'rovi uchun: { data, error, loading, reload }
// reload() ma'lumot bor bo'lsa sahifani miltillatmasdan jimgina yangilaydi.
export function useApi(path) {
  const [state, setState] = useState({ path: null, data: null, error: null })
  const load = useCallback(() => {
    let alive = true
    api(path)
      .then((data) => alive && setState({ path, data, error: null }))
      .catch((error) => alive && setState({ path, data: null, error }))
    return () => { alive = false }
  }, [path])
  useEffect(() => load(), [load])
  const current = state.path === path
  return {
    data: current ? state.data : null,
    error: current ? state.error : null,
    loading: !current,
    reload: load,
  }
}
