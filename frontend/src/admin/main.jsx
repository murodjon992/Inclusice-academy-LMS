import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import AdminApp from './AdminApp'
import { AuthProvider } from '../lib/auth'

createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <AuthProvider>
      <AdminApp />
    </AuthProvider>
  </BrowserRouter>
)
