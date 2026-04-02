import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
// https://vite.dev/config/
export default defineConfig({
  plugins: [react(),   tailwindcss(),],
  base: "/static/frontend", // important for Django + SPA at /

  build: {
    outDir: "../cypress/static/frontend",
    emptyOutDir: true,
    manifest: false, // optional, keep simple unless you need it
  },
  server: {
    proxy: {
      "/api": "http://localhost:8000",
    }
  }
}
)
