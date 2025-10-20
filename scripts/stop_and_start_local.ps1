Param(
  [string]$PROJECT_ROOT = 'C:\Users\Apoor\ai-active-learning-platform-1'
)

Set-Location $PROJECT_ROOT

Write-Output 'Checking processes listening on ports 5000 and 3000'
Get-NetTCPConnection -LocalPort 5000,3000 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess | Format-Table -AutoSize

Write-Output 'If you want to kill a PID, run Stop-Process -Id <PID> -Force manually.'

Write-Output 'Activate venv311 and start backend in this terminal (foreground):'
Write-Output '& .\venv311\Scripts\Activate.ps1; $env:ENABLE_HF_BACKGROUND=\'1\'; python .\backend\main.py'

Write-Output 'Start frontend in separate terminal (run these commands in a new PowerShell window):'
Write-Output 'cd frontend; npm ci; npm start'
