module.exports = {
  apps: [
    {
      name: 'claude-office-ui',
      cwd: '/mnt/e_drive/claude-office/src/ui',
      script: 'npm',
      args: 'run dev',
      env: {
        NODE_ENV: 'development',
        PORT: 8055,
      },
      watch: false,
      autorestart: true,
      restart_delay: 1000,
      max_restarts: 10,
    },
    {
      name: 'claude-office-monitor',
      cwd: '/mnt/e_drive/claude-office/src/session-monitor',
      script: 'index.js',
      env: {
        NODE_ENV: 'development',
        PORT: 8053,
      },
      watch: false,
      autorestart: true,
      restart_delay: 1000,
      max_restarts: 10,
    },
  ],
};
