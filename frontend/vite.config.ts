import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
// Routes all API requests starting with /api to the backend server running on http://localhost:8000
export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  test: {
    environment: 'jsdom',
  },
  server: {
    proxy: {
      '/api':{
        target: 'http://localhost:8000',
        changeOrigin: true,      
      }
    }
  }
})
