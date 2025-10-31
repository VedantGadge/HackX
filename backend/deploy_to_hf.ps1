# Deploy backend to Hugging Face Spaces
# Space URL: https://huggingface.co/spaces/Lamaq/signlink-hackx

Write-Host "🚀 Deploying SignLink Backend to Hugging Face Spaces" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is available
try {
    git --version | Out-Null
} catch {
    Write-Host "❌ Git is not installed. Please install git first." -ForegroundColor Red
    exit 1
}

# Space repository URL
$SPACE_REPO = "https://huggingface.co/spaces/Lamaq/signlink-hackx"
$SPACE_GIT = "https://huggingface.co/spaces/Lamaq/signlink-hackx.git"

Write-Host "📦 Preparing files for deployment..." -ForegroundColor Yellow
Write-Host ""

# Create temporary directory for deployment
$TEMP_DIR = New-Item -ItemType Directory -Path $env:TEMP -Name "signlink-deploy-$(Get-Random)" -Force
Write-Host "📂 Using temporary directory: $TEMP_DIR" -ForegroundColor Gray

# Copy backend files
Write-Host "📋 Copying backend files..." -ForegroundColor Yellow

$itemsToCopy = @(
    "app",
    "services",
    "utils",
    "models",
    "pretrained",
    "mapper",
    "requirements.txt",
    "Dockerfile",
    "README.md",
    "start.py"
)

foreach ($item in $itemsToCopy) {
    if (Test-Path $item) {
        Copy-Item -Path $item -Destination $TEMP_DIR -Recurse -Force
        Write-Host "  ✓ Copied $item" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Skipped $item (not found)" -ForegroundColor Yellow
    }
}

# Copy .dockerignore if exists
if (Test-Path ".dockerignore") {
    Copy-Item -Path ".dockerignore" -Destination $TEMP_DIR -Force
}

# Create outputs and videos directories
New-Item -ItemType Directory -Path "$TEMP_DIR\outputs" -Force | Out-Null
New-Item -ItemType Directory -Path "$TEMP_DIR\videos" -Force | Out-Null

Write-Host ""
Write-Host "✅ Files copied to temporary directory" -ForegroundColor Green
Write-Host ""

# Initialize git repository
Push-Location $TEMP_DIR

git init
git remote add space $SPACE_GIT

Write-Host "📝 Creating commit..." -ForegroundColor Yellow
git add .
git commit -m "Deploy SignLink backend to Hugging Face Spaces"

Write-Host ""
Write-Host "🔐 Pushing to Hugging Face Spaces..." -ForegroundColor Cyan
Write-Host "You will be prompted for your Hugging Face credentials." -ForegroundColor Yellow
Write-Host "Username: Your HF username (Lamaq)" -ForegroundColor White
Write-Host "Password: Use your HF Access Token (not your password!)" -ForegroundColor White
Write-Host ""
Write-Host "Get your token from: https://huggingface.co/settings/tokens" -ForegroundColor Cyan
Write-Host ""

git push --force space main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Your Space is available at:" -ForegroundColor Cyan
    Write-Host "   $SPACE_REPO" -ForegroundColor White
    Write-Host ""
    Write-Host "⚠️  IMPORTANT NEXT STEPS:" -ForegroundColor Yellow
    Write-Host "1. Go to Space Settings: $SPACE_REPO/settings" -ForegroundColor White
    Write-Host "2. Navigate to 'Variables and secrets'" -ForegroundColor White
    Write-Host "3. Add environment variable:" -ForegroundColor White
    Write-Host "   Name: OPENAI_API_KEY" -ForegroundColor Cyan
    Write-Host "   Value: your-openai-api-key" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "4. Wait for Space to build (5-10 minutes)" -ForegroundColor White
    Write-Host "5. Test the API:" -ForegroundColor White
    Write-Host "   curl https://lamaq-signlink-hackx.hf.space/health" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📚 API Documentation will be available at:" -ForegroundColor Cyan
    Write-Host "   https://lamaq-signlink-hackx.hf.space/docs" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Please check your credentials and try again." -ForegroundColor Yellow
    Write-Host ""
}

# Cleanup
Pop-Location
Remove-Item -Path $TEMP_DIR -Recurse -Force

Write-Host "🧹 Cleaned up temporary files" -ForegroundColor Gray
Write-Host ""
Write-Host "Done! 🎉" -ForegroundColor Green
