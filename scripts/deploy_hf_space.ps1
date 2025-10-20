Param(
  [string]$HF_USER = 'Apoorv048',
  [string]$HF_SPACE = 'ai-active-learning-platform',
  [string]$LOCAL_REPO_ROOT = 'C:\Users\Apoor\ai-active-learning-platform-1'
)

if (-not $env:HF_TOKEN -or $env:HF_TOKEN -eq '') {
  Write-Error "HF_TOKEN environment variable is not set. Run: $env:HF_TOKEN='your_token_here' in this PowerShell session and re-run this script."
  exit 1
}

$HF_TOKEN = $env:HF_TOKEN
$cloneUrl = "https://$HF_USER`:$HF_TOKEN@huggingface.co/spaces/$HF_USER/$HF_SPACE"

Write-Output "Cloning Hugging Face Space repo: $HF_USER/$HF_SPACE"
git clone $cloneUrl
if ($LASTEXITCODE -ne 0) { Write-Error 'git clone failed'; exit 1 }

Set-Location -Path "./$HF_SPACE"

Write-Output 'Syncing backend files into Space repo...'
robocopy "$LOCAL_REPO_ROOT\backend" ".\backend" /MIR | Out-Null

Copy-Item "$LOCAL_REPO_ROOT\backend\main.py" -Destination ".\backend\main.py" -Force
Copy-Item "$LOCAL_REPO_ROOT\backend\requirements.txt" -Destination ".\backend\requirements.txt" -Force

Set-Content -Path .\Procfile -Value 'web: python backend/main.py' -Force

git add -A
git commit -m "Add backend code for Hugging Face Space" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Output 'No changes to commit or commit had non-zero exit (might be no-op).'
}

Write-Output 'Pushing changes to the Space (main branch)...'
git push origin main
if ($LASTEXITCODE -ne 0) { Write-Error 'git push failed'; exit 1 }

Write-Output 'Push complete. Visit your Space in the Hugging Face UI to watch the build logs.'
Write-Output "Space URL (estimated): https://$HF_USER-$HF_SPACE.hf.space"
