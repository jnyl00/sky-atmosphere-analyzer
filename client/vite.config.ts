import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev proxy: routes /api/* to backend (adjust BACKEND_URL via env if needed)
const backendUrl = process.env.VITE_BACKEND_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: backendUrl,
        changeOrigin: true,
      },
    },
  },
  resolve: {
    alias: {
      '@': '/src',
    },
  },
})
