import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/db': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/data': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/datasets': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/user': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'react-router-dom']
  }
}) 