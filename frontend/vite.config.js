import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/react/') ||
              id.includes('node_modules/react-dom/') ||
              id.includes('node_modules/react-router-dom/')) {
            return 'react-vendor'
          }
          if (id.includes('node_modules/framer-motion/')) {
            return 'motion'
          }
          if (id.includes('node_modules/recharts/')) {
            return 'charts'
          }
          if (id.includes('node_modules/d3') ||
              id.includes('node_modules/topojson-client/')) {
            return 'maps'
          }
          if (id.includes('node_modules/lucide-react/')) {
            return 'ui'
          }
        }
      }
    }
  }
})