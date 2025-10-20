Param(
  [string]$FRONTEND_DIR = 'C:\Users\Apoor\ai-active-learning-platform-1\frontend'
)

if (-not $env:VERCEL_TOKEN -or $env:VERCEL_TOKEN -eq '') {
  Write-Error "VERCEL_TOKEN environment variable not set. Set it and re-run."
  exit 1
}

Set-Location -Path $FRONTEND_DIR

Write-Output 'Installing frontend dependencies and building...'
npm ci
npm run build

Write-Output 'Deploying to Vercel (requires VERCEL_TOKEN and previously configured project/org IDs)'
# Deploy with automatic detection
npx vercel --prod --confirm --token $env:VERCEL_TOKEN
