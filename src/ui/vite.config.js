import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 8055,
    strictPort: true, // 端口被占用時報錯，不自動跳
  },
  build: {
    outDir: 'dist',
  },
});
