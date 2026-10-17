import React from 'react'
import { Route, Routes } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import AdminLayout from './AdminLayout'
import Dashboard from './Dashboard'
import ResourceList from './ResourceList'
import ResourceForm from './ResourceForm'
import Progress from './Progress'

const centered = { display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', flexDirection: 'column' }

export default function AdminApp() {
  const { user, ready } = useAuth()
  if (!ready) return <div style={centered}><div className="spinner-border text-primary" role="status"></div></div>
  if (!user) {
    window.location.replace('/login-user/?next=/manage-admin/')
    return null
  }
  if (!user.is_admin) {
    return (
      <div style={centered}>
        <h3>Ruxsat yo'q</h3>
        <p className="text-muted">Bu sahifa faqat administrator uchun.</p>
        <a href="/" className="btn btn-primary">Saytga qaytish</a>
      </div>
    )
  }
  return (
    <Routes>
      <Route element={<AdminLayout />}>
        <Route path="/manage-admin/" element={<Dashboard />} />
        <Route path="/manage-admin/progress" element={<Progress />} />
        <Route path="/manage-admin/r/:key" element={<ResourceList />} />
        <Route path="/manage-admin/r/:key/new" element={<ResourceForm />} />
        <Route path="/manage-admin/r/:key/:id" element={<ResourceForm />} />
        <Route path="*" element={<Dashboard />} />
      </Route>
    </Routes>
  )
}
