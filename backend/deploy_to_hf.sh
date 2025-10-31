#!/bin/bash
# Deploy backend to Hugging Face Spaces
# Space URL: https://huggingface.co/spaces/Lamaq/signlink-hackx

echo "🚀 Deploying SignLink Backend to Hugging Face Spaces"
echo "===================================================="
echo ""

# Check if git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Space repository URL
SPACE_REPO="https://huggingface.co/spaces/Lamaq/signlink-hackx"
SPACE_GIT="https://huggingface.co/spaces/Lamaq/signlink-hackx.git"

echo "📦 Preparing files for deployment..."
echo ""

# Create temporary directory for deployment
TEMP_DIR=$(mktemp -d)
echo "📂 Using temporary directory: $TEMP_DIR"

# Copy backend files
echo "📋 Copying backend files..."
cp -r app/ $TEMP_DIR/
cp -r services/ $TEMP_DIR/
cp -r utils/ $TEMP_DIR/
cp -r models/ $TEMP_DIR/
cp -r pretrained/ $TEMP_DIR/
cp -r mapper/ $TEMP_DIR/
cp requirements.txt $TEMP_DIR/
cp Dockerfile $TEMP_DIR/
cp README.md $TEMP_DIR/
cp start.py $TEMP_DIR/
cp .dockerignore $TEMP_DIR/ 2>/dev/null || true

# Create outputs and videos directories (will be populated at runtime)
mkdir -p $TEMP_DIR/outputs
mkdir -p $TEMP_DIR/videos

echo "✅ Files copied to temporary directory"
echo ""

# Initialize git repository
cd $TEMP_DIR
git init
git remote add space $SPACE_GIT

echo "📝 Creating commit..."
git add .
git commit -m "Deploy SignLink backend to Hugging Face Spaces"

echo ""
echo "🔐 Pushing to Hugging Face Spaces..."
echo "You will be prompted for your Hugging Face credentials."
echo "Username: Your HF username (Lamaq)"
echo "Password: Use your HF Access Token (not your password!)"
echo ""
echo "Get your token from: https://huggingface.co/settings/tokens"
echo ""

git push --force space main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🌐 Your Space is available at:"
    echo "   $SPACE_REPO"
    echo ""
    echo "⚠️  IMPORTANT NEXT STEPS:"
    echo "1. Go to Space Settings: $SPACE_REPO/settings"
    echo "2. Navigate to 'Variables and secrets'"
    echo "3. Add environment variable:"
    echo "   Name: OPENAI_API_KEY"
    echo "   Value: your-openai-api-key"
    echo ""
    echo "4. Wait for Space to build (5-10 minutes)"
    echo "5. Test the API:"
    echo "   curl https://lamaq-signlink-hackx.hf.space/health"
    echo ""
    echo "📚 API Documentation will be available at:"
    echo "   https://lamaq-signlink-hackx.hf.space/docs"
    echo ""
else
    echo ""
    echo "❌ Deployment failed!"
    echo "Please check your credentials and try again."
    echo ""
fi

# Cleanup
cd -
rm -rf $TEMP_DIR

echo "🧹 Cleaned up temporary files"
echo ""
echo "Done! 🎉"
