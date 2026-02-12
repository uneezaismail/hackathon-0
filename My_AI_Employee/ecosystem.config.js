module.exports = {
  apps: [
    // Gold Tier Architecture: Orchestrator + Process Watchdog
    // Orchestrator manages all watchers (Gmail, WhatsApp, LinkedIn, filesystem)
    // Process Watchdog monitors orchestrator health and auto-restarts on crash
    {
      name: 'orchestrator',
      script: 'uv',
      args: ['run', 'python', 'orchestrator.py'],
      cwd: '/mnt/d/hackathon-0/My_AI_Employee',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/orchestrator-error.log',
      out_file: 'logs/orchestrator-out.log',
      env: {
        PYTHONUNBUFFERED: '1',
        VAULT_ROOT: 'AI_Employee_Vault',
        DRY_RUN: 'true'
      }
    },
    {
      name: 'process-watchdog',
      script: 'uv',
      args: ['run', 'python', 'process_watchdog.py'],
      cwd: '/mnt/d/hackathon-0/My_AI_Employee',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      min_uptime: '10s',
      error_file: 'logs/process-watchdog-error.log',
      out_file: 'logs/process-watchdog-out.log',
      env: {
        PYTHONUNBUFFERED: '1',
        WATCHDOG_CHECK_INTERVAL: '60',
        WATCHDOG_MAX_RESTARTS: '3',
        WATCHDOG_RESTART_WINDOW: '300'
      }
    }
  ]
};
