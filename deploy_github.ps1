param (
    [string]$Username
)

if (-not $Username) {
    $Username = Read-Host "Enter your GitHub username"
}

if (-not $Username) {
    Write-Error "GitHub username cannot be empty."
    exit 1
}

$RepoUrl = "https://github.com/$Username/google-photos-anchorjump.git"
Write-Host "Configuring remote origin: $RepoUrl" -ForegroundColor Cyan

git remote remove origin 2>$null
git remote add origin $RepoUrl
git branch -M main

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nSuccessfully pushed to $RepoUrl!" -ForegroundColor Green
    Write-Host "`nNext Step for Streamlit Cloud:" -ForegroundColor Yellow
    Write-Host "1. Go to https://share.streamlit.io"
    Write-Host "2. Click 'Create app'"
    Write-Host "3. Repository: $Username/google-photos-anchorjump"
    Write-Host "4. Branch: main"
    Write-Host "5. Main file path: app.py"
    Write-Host "6. Advanced settings > Secrets -> Add: GEMINI_API_KEY = 'your_key'"
    Write-Host "7. Click 'Deploy!'"
} else {
    Write-Error "Push failed. Please ensure the repository 'google-photos-anchorjump' is created on GitHub."
}
