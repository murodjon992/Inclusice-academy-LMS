import React, { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { api } from './api'

const AuthContext = createContext(null)
export const useAuth = () => useContext(AuthContext)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)

  const refresh = useCallback(async () => {
    try {
      const d = await api('/auth/me/')
      setUser(d.user)
    } catch {
      setUser(null)
    } finally {
      setReady(true)
    }
  }, [])
  useEffect(() => { refresh() }, [refresh])

  const login = async (username, password) => {
    const d = await api('/auth/login/', { method: 'POST', body: { username, password } })
    setUser(d.user)
    return d.user
  }
  const register = async (payload) => {
    const d = await api('/auth/register/', { method: 'POST', body: payload })
    setUser(d.user)
    return d.user
  }
  const logout = async () => {
    await api('/auth/logout/', { method: 'POST' })
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, setUser, ready, login, register, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  )
}
