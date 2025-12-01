#!/bin/bash

# CrowdLib Project Initialization Script
# This script sets up the development environment for the CrowdLib project (Django + React)
# Run this script after cloning the repository: bash init.sh
# Disclosure: This script was AI Generated

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running on supported OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        log_info "Detected Linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        log_info "Detected macOS"
    else
        log_warning "This script is optimized for macOS and Linux. Windows users should run init.bat."
    fi
}

# Check if required commands are available
check_prerequisites() {
    log_info "Checking prerequisites..."

    local missing_deps=0

    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed. Please install Python 3.8 or higher."
        missing_deps=1
    else
        log_success "Python 3 found: $(python3 --version)"
    fi

    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed. Please install Node.js 16 or higher."
        missing_deps=1
    else
        log_success "Node.js found: $(node --version)"
    fi

    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed. Please install npm."
        missing_deps=1
    else
        log_success "npm found: $(npm --version)"
    fi

    if [ $missing_deps -eq 1 ]; then
        log_error "Please install missing dependencies and run the script again."
        exit 1
    fi
}

# Setup backend
setup_backend() {
    log_info "Setting up backend environment..."

    cd backend

    # Check if Python virtual environment exists
    if [ ! -d "venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv venv
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi

    # Activate virtual environment
    log_info "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel > /dev/null 2>&1

    # Install Python dependencies
    log_info "Installing Python dependencies from requirements.txt..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "Python dependencies installed"
    else
        log_error "requirements.txt not found in backend directory"
        exit 1
    fi

    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_warning ".env file not found in backend directory"
        log_info "Please create a .env file with the required environment variables."
        log_info "You can copy from an existing .env file or create one manually."
        log_info "Required variables: MONGODB_CLIENT_USERNAME, MONGODB_CLIENT_PASSWORD, DJANGO_SETTINGS_MODULE, etc."
    else
        log_success ".env file found"
    fi

    # Run Django migrations
    log_info "Running Django migrations..."
    python manage.py migrate --noinput 2>/dev/null || log_warning "Could not run migrations (this may be normal if database is not yet set up)"

    log_success "Backend setup complete"
    cd ..
}

# Setup frontend
setup_frontend() {
    log_info "Setting up frontend environment..."

    cd frontend

    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
        log_success "Node.js dependencies installed"
    else
        log_success "Node.js dependencies already exist"
        log_info "Running npm install to ensure packages are up to date..."
        npm install
    fi

    log_success "Frontend setup complete"
    cd ..
}

# Create .env example if it doesn't exist
create_env_example() {
    if [ ! -f "backend/.env.example" ]; then
        log_info "Creating .env.example file in backend directory..."
        cat > backend/.env.example << 'EOF'
# MongoDB Configuration
MONGODB_CLIENT_USERNAME=your_mongodb_username
MONGODB_CLIENT_PASSWORD=your_mongodb_password
MONGODB_DB_NAME=crowdlib

# Django Configuration
DJANGO_SETTINGS_MODULE=backend.settings

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=crowdlib-image-bucket
AWS_REGION=us-east-2
AWS_S3_URL=https://crowdlib-image-bucket.s3.amazonaws.com

# Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key
EOF
        log_success ".env.example created"
    fi
}

# Print usage instructions
print_instructions() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Setup Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "To start developing:"
    echo ""
    echo "1. Backend (Django):"
    echo "   cd backend"
    echo "   source venv/bin/activate"
    echo "   python manage.py runserver"
    echo ""
    echo "2. Frontend (React):"
    echo "   cd frontend"
    echo "   npm run dev"
    echo ""
    echo "3. To deactivate the Python virtual environment:"
    echo "   deactivate"
    echo ""
    echo -e "${YELLOW}Important:${NC}"
    echo "- Make sure you have a valid .env file in the backend directory"
    echo "- The database must be accessible for Django migrations to work"
    echo "- Frontend will typically run on http://localhost:5173"
    echo "- Backend will typically run on http://localhost:8000"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   CrowdLib Project Initialization      ║"
    echo "║   Django + React Development Setup     ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""

    check_os
    check_prerequisites

    echo ""
    create_env_example
    setup_backend

    echo ""
    setup_frontend

    echo ""
    print_instructions
}

# Run main function
main
