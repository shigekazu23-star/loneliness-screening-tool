import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev server proxies /api to the Flask backend on port 5000, so the
// browser talks to one origin (mirrors the layered architecture).
export default defineConfig({
  plugins: [react()],
  // Force the automatic JSX runtime at the esbuild level as well, so the
  // app renders even if the react plugin transform is skipped.
  esbuild: { jsx: 'automatic' },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000',
    },
  },
})
