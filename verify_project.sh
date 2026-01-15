#!/bin/bash
# Project verification script
# Checks that all required files and directories exist

set -e

echo "======================================"
echo "AI Text Spotter - Project Verification"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1"
        return 0
    else
        echo -e "${RED}✗${NC} $1 (missing)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} $1/"
        return 0
    else
        echo -e "${RED}✗${NC} $1/ (missing)"
        return 1
    fi
}

ERRORS=0

# Root files
echo "Checking root files..."
check_file "README.md" || ((ERRORS++))
check_file "QUICKSTART.md" || ((ERRORS++))
check_file "TESTING.md" || ((ERRORS++))
check_file "CONTRIBUTING.md" || ((ERRORS++))
check_file "LICENSE" || ((ERRORS++))
check_file ".gitignore" || ((ERRORS++))
check_file "docker-compose.yml" || ((ERRORS++))
check_file "nginx.conf" || ((ERRORS++))
echo ""

# Backend structure
echo "Checking backend structure..."
check_dir "backend" || ((ERRORS++))
check_dir "backend/app" || ((ERRORS++))
check_dir "backend/app/api" || ((ERRORS++))
check_dir "backend/app/detectors" || ((ERRORS++))
check_dir "backend/app/services" || ((ERRORS++))
check_dir "backend/app/models" || ((ERRORS++))
check_dir "backend/tests" || ((ERRORS++))
echo ""

# Backend files
echo "Checking backend files..."
check_file "backend/requirements.txt" || ((ERRORS++))
check_file "backend/Dockerfile" || ((ERRORS++))
check_file "backend/.env.example" || ((ERRORS++))
check_file "backend/app/__init__.py" || ((ERRORS++))
check_file "backend/app/main.py" || ((ERRORS++))
check_file "backend/app/config.py" || ((ERRORS++))
check_file "backend/app/api/__init__.py" || ((ERRORS++))
check_file "backend/app/api/routes.py" || ((ERRORS++))
check_file "backend/app/detectors/__init__.py" || ((ERRORS++))
check_file "backend/app/detectors/mathematical.py" || ((ERRORS++))
check_file "backend/app/detectors/llm_detector.py" || ((ERRORS++))
check_file "backend/app/detectors/jury.py" || ((ERRORS++))
check_file "backend/app/services/__init__.py" || ((ERRORS++))
check_file "backend/app/services/text_processor.py" || ((ERRORS++))
check_file "backend/app/services/file_handler.py" || ((ERRORS++))
check_file "backend/app/models/__init__.py" || ((ERRORS++))
check_file "backend/app/models/schemas.py" || ((ERRORS++))
check_file "backend/tests/__init__.py" || ((ERRORS++))
check_file "backend/tests/test_core.py" || ((ERRORS++))
echo ""

# Frontend structure
echo "Checking frontend structure..."
check_dir "frontend" || ((ERRORS++))
check_dir "frontend/css" || ((ERRORS++))
check_dir "frontend/js" || ((ERRORS++))
check_dir "frontend/assets" || ((ERRORS++))
echo ""

# Frontend files
echo "Checking frontend files..."
check_file "frontend/index.html" || ((ERRORS++))
check_file "frontend/css/styles.css" || ((ERRORS++))
check_file "frontend/js/main.js" || ((ERRORS++))
check_file "frontend/js/api.js" || ((ERRORS++))
check_file "frontend/js/fileHandler.js" || ((ERRORS++))
check_file "frontend/js/textDisplay.js" || ((ERRORS++))
check_file "frontend/js/export.js" || ((ERRORS++))
check_file "frontend/assets/.gitkeep" || ((ERRORS++))
echo ""

# Examples
echo "Checking examples..."
check_dir "examples" || ((ERRORS++))
check_file "examples/README.md" || ((ERRORS++))
check_file "examples/human_written.txt" || ((ERRORS++))
check_file "examples/ai_generated.txt" || ((ERRORS++))
check_file "examples/mixed.txt" || ((ERRORS++))
echo ""

# Models directory
echo "Checking models directory..."
check_dir "models" || ((ERRORS++))
check_file "models/.gitkeep" || ((ERRORS++))
echo ""

# Summary
echo "======================================"
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All files and directories present!${NC}"
    echo "======================================"
    exit 0
else
    echo -e "${RED}✗ $ERRORS missing files or directories${NC}"
    echo "======================================"
    exit 1
fi
