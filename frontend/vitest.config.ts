import { defineConfig } from 'vitest/config'
import viteReact from '@vitejs/plugin-react'
import viteTsConfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [viteReact(), viteTsConfigPaths()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: [], // Add setup file if needed later
  },
})
