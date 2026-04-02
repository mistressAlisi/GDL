#!/bin/bash

# BETANY LOTTO - Build and Deploy to Django Static Folder
# This script builds the React app and copies it to Django's static folder

set -e  # Exit on error

echo "🎰 BETANY LOTTO - Build and Deploy Script"
echo "=========================================="

# Configuration
DJANGO_PROJECT_PATH="${DJANGO_PROJECT_PATH:-../django-betany-lotto}"
DJANGO_STATIC_PATH="${DJANGO_PROJECT_PATH}/static"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Django path exists
if [ ! -d "$DJANGO_PROJECT_PATH" ]; then
    echo -e "${RED}❌ Django project not found at: ${DJANGO_PROJECT_PATH}${NC}"
    echo -e "${YELLOW}💡 Set DJANGO_PROJECT_PATH environment variable:${NC}"
    echo "   export DJANGO_PROJECT_PATH=/path/to/your/django-project"
    echo "   Or edit this script to set the correct path"
    exit 1
fi

# Step 1: Clean previous build
echo -e "\n${YELLOW}🧹 Cleaning previous build...${NC}"
rm -rf dist/

# Step 2: Install dependencies (optional, comment out if not needed)
# echo -e "\n${YELLOW}📦 Installing dependencies...${NC}"
# npm install

# Step 3: Build React app
echo -e "\n${YELLOW}🔨 Building React application...${NC}"
npm run build

if [ ! -d "dist" ]; then
    echo -e "${RED}❌ Build failed - dist/ folder not created${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build complete${NC}"

# Step 4: Clear Django static folder
echo -e "\n${YELLOW}🗑️  Clearing Django static folder...${NC}"
if [ -d "$DJANGO_STATIC_PATH" ]; then
    # Keep .gitkeep or .gitignore if they exist
    find "$DJANGO_STATIC_PATH" -mindepth 1 ! -name '.gitkeep' ! -name '.gitignore' -delete
else
    mkdir -p "$DJANGO_STATIC_PATH"
fi

# Step 5: Copy build to Django
echo -e "\n${YELLOW}📦 Copying build to Django static folder...${NC}"
cp -r dist/* "$DJANGO_STATIC_PATH/"

echo -e "${GREEN}✅ Files copied to: ${DJANGO_STATIC_PATH}${NC}"

# Step 6: Collect static files in Django (optional)
echo -e "\n${YELLOW}📚 Collecting Django static files...${NC}"
read -p "Run Django collectstatic? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd "$DJANGO_PROJECT_PATH"
    python manage.py collectstatic --noinput
    echo -e "${GREEN}✅ Static files collected${NC}"
    cd - > /dev/null
else
    echo -e "${YELLOW}⚠️  Skipped collectstatic${NC}"
fi

# Summary
echo -e "\n${GREEN}=========================================="
echo -e "✅ Deployment Complete!"
echo -e "==========================================${NC}"
echo -e "\nNext steps:"
echo -e "1. Start Django server: ${YELLOW}cd ${DJANGO_PROJECT_PATH} && python manage.py runserver${NC}"
echo -e "2. Start Daphne for WebSockets: ${YELLOW}daphne -p 8000 your_project.asgi:application${NC}"
echo -e "3. Visit: ${YELLOW}http://localhost:8000${NC}"
echo ""
