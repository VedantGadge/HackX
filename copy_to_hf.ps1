# Copy Backend Files to Hugging Face Spaces Repository
# Run this from: C:\Users\lamaq\OneDrive\Desktop\MUJ REPO

# Set paths
$SOURCE = "C:\Users\lamaq\OneDrive\Desktop\MUJ REPO\backend"
$DEST = "C:\Users\lamaq\OneDrive\Desktop\MUJ REPO\signlink-hackx"

Write-Host "📦 Copying backend files to HF Spaces repo..." -ForegroundColor Cyan
Write-Host ""

# Copy directories
Write-Host "📁 Copying directories..." -ForegroundColor Yellow
Copy-Item -Path "$SOURCE\app" -Destination "$DEST\app" -Recurse -Force
Write-Host "  ✓ Copied app/" -ForegroundColor Green

Copy-Item -Path "$SOURCE\services" -Destination "$DEST\services" -Recurse -Force
Write-Host "  ✓ Copied services/" -ForegroundColor Green

Copy-Item -Path "$SOURCE\utils" -Destination "$DEST\utils" -Recurse -Force
Write-Host "  ✓ Copied utils/" -ForegroundColor Green

Copy-Item -Path "$SOURCE\models" -Destination "$DEST\models" -Recurse -Force
Write-Host "  ✓ Copied models/" -ForegroundColor Green

Copy-Item -Path "$SOURCE\pretrained" -Destination "$DEST\pretrained" -Recurse -Force
Write-Host "  ✓ Copied pretrained/" -ForegroundColor Green

Copy-Item -Path "$SOURCE\mapper" -Destination "$DEST\mapper" -Recurse -Force
Write-Host "  ✓ Copied mapper/" -ForegroundColor Green

# Copy files
Write-Host ""
Write-Host "📄 Copying configuration files..." -ForegroundColor Yellow
Copy-Item -Path "$SOURCE\requirements.txt" -Destination "$DEST\requirements.txt" -Force
Write-Host "  ✓ Copied requirements.txt" -ForegroundColor Green

Copy-Item -Path "$SOURCE\Dockerfile" -Destination "$DEST\Dockerfile" -Force
Write-Host "  ✓ Copied Dockerfile" -ForegroundColor Green

Copy-Item -Path "$SOURCE\README.md" -Destination "$DEST\README.md" -Force
Write-Host "  ✓ Copied README.md" -ForegroundColor Green

Copy-Item -Path "$SOURCE\start.py" -Destination "$DEST\start.py" -Force
Write-Host "  ✓ Copied start.py" -ForegroundColor Green

# Copy .dockerignore if exists
if (Test-Path "$SOURCE\.dockerignore") {
    Copy-Item -Path "$SOURCE\.dockerignore" -Destination "$DEST\.dockerignore" -Force
    Write-Host "  ✓ Copied .dockerignore" -ForegroundColor Green
}

Write-Host ""
Write-Host "ℹ️ Note: Output/video storage uses /tmp (ephemeral) - no persistent directories needed" -ForegroundColor Cyan

Write-Host ""
Write-Host "✅ All files copied successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📝 Next steps:" -ForegroundColor Cyan
Write-Host "1. cd signlink-hackx" -ForegroundColor White
Write-Host "2. git add ." -ForegroundColor White
Write-Host "3. git commit -m 'Deploy SignLink backend'" -ForegroundColor White
Write-Host "4. git push" -ForegroundColor White
Write-Host ""
Write-Host "🔐 Don't forget to set OPENAI_API_KEY in Space settings!" -ForegroundColor Yellow
