import { defineConfig } from 'vite';

export default defineConfig({
  publicDir: 'public',
  server: {
    host: '0.0.0.0',
    port: 8055,
    strictPort: true,
    fs: {
      strict: false,
    }
  },
  build: {
    outDir: 'dist',
  },
});
