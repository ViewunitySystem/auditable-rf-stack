import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/auditable-rf-stack/',
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    host: true,
    open: true
  },
  preview: {
    port: 3000,
    host: true,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@radix-ui/react-slot', '@radix-ui/react-tabs', '@radix-ui/react-select', '@radix-ui/react-switch', '@radix-ui/react-slider', '@radix-ui/react-checkbox', '@radix-ui/react-tooltip', '@radix-ui/react-dialog', '@radix-ui/react-collapsible', '@radix-ui/react-progress', '@radix-ui/react-label'],
          charts: ['recharts'],
          motion: ['framer-motion']
        }
      }
    }
  }
})
