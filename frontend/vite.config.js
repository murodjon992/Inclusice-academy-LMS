import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev: http://localhost:5173 (Django http://127.0.0.1:8000 da ishlab turishi kerak).
//   Sayt:  http://localhost:5173/        Admin: http://localhost:5173/manage-admin/
// Build: ../static/app/ ichiga app.js, app.css (sayt) va admin.js (admin panel) yoziladi.
const DJANGO = 'http://127.0.0.1:8000'

// Dev rejimida /manage-admin/... manzillariga admin.html ni beradi
const adminHtml = () => ({
  name: 'admin-html',
  configureServer(server) {
    server.middlewares.use((req, _res, next) => {
      if (req.url && req.url.startsWith('/manage-admin')) req.url = '/admin.html'
      next()
    })
  },
})

export default defineConfig({
  plugins: [react(), adminHtml()],
  server: {
    port: 5173,
    proxy: {
      '/api': DJANGO,
      '/media': DJANGO,
      '/static': DJANGO,
      '/admin/': DJANGO,
      '/logout': DJANGO,
      '/certificate': DJANGO,
      '/kutubxona/file': DJANGO,
    },
  },
  build: {
    outDir: '../static/app',
    emptyOutDir: true,
    rollupOptions: {
      input: { app: 'src/main.jsx', admin: 'src/admin/main.jsx' },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: 'chunk-[name]-[hash].js',
        assetFileNames: (a) => (a.name && a.name.endsWith('.css') ? 'app.css' : 'assets/[name][extname]'),
      },
    },
  },
})
