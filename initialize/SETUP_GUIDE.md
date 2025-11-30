# CrowdLib Development Setup Guide

Complete step-by-step instructions for setting up the CrowdLib development environment on macOS, Linux, and Windows.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Automated Setup (macOS/Linux)](#automated-setup-macoslinux)
3. [Manual Setup (All Platforms)](#manual-setup-all-platforms)
4. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python 3.8 or higher**
- **Node.js 16 or higher**
- **npm** (bundled with Node.js)
- **Git**

### Installation Instructions

#### macOS
```bash
# Using Homebrew (install Homebrew from https://brew.sh/ first)
brew install python@3.11
brew install node
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
sudo apt install nodejs npm
```

#### Windows
1. **Python**: Download and install from [python.org](https://www.python.org/downloads/)
   - ⚠️ **Important**: Check "Add Python to PATH" during installation
2. **Node.js**: Download and install from [nodejs.org](https://nodejs.org/)

### Verify Installation
```bash
python3 --version  # Should be 3.8+
node --version     # Should be 16+
npm --version      # Should be 7+
git --version      # Should be 2+
```

## Automated Setup (macOS/Linux)

For macOS and Linux users, the quickest way to set up is using the provided initialization script.

### Steps

1. **Clone the repository** (if you haven't already)
   ```bash
   git clone <repository-url>
   cd CrowdLib
   ```

2. **Run the initialization script**
   ```bash
   bash init.sh
   ```

3. **Configure environment variables**
   - Copy `backend/.env.example` to `backend/.env`
   - Edit `backend/.env` with your actual credentials

4. **Start developing**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   python manage.py runserver

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

### What init.sh Does
- ✓ Checks for Python 3, Node.js, and npm
- ✓ Creates a Python virtual environment in `backend/venv`
- ✓ Installs all Python packages from `requirements.txt`
- ✓ Installs all npm packages from `frontend/package.json`
- ✓ Creates `backend/.env.example` as a template
- ✓ Attempts to run Django migrations (if database is available)

## Manual Setup (All Platforms)

Follow these instructions for step-by-step manual setup on any platform.

### Backend Setup (Django)

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment**
   ```bash
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate

   # Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Upgrade pip, setuptools, and wheel**
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env  # Windows: copy .env.example .env

   # Edit .env with your actual values (use your favorite text editor)
   ```

6. **Run Django migrations**
   ```bash
   python manage.py migrate
   ```

7. **Start the Django development server**
   ```bash
   python manage.py runserver
   ```
   The server will be available at `http://localhost:8000`

### Frontend Setup (React)

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the Vite development server**
   ```bash
   npm run dev
   ```
   The dev server will typically be available at `http://localhost:5173`

### Environment Variables

Create a `backend/.env` file with the following variables:

```
MONGODB_CLIENT_USERNAME=<your_username>
MONGODB_CLIENT_PASSWORD=<your_password>
MONGODB_DB_NAME=crowdlib
DJANGO_SETTINGS_MODULE=backend.settings
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
AWS_ACCESS_KEY_ID=<your_aws_key>
AWS_SECRET_ACCESS_KEY=<your_aws_secret>
AWS_STORAGE_BUCKET_NAME=crowdlib-image-bucket
AWS_REGION=us-east-2
AWS_S3_URL=https://crowdlib-image-bucket.s3.amazonaws.com
GEMINI_API_KEY=<your_gemini_api_key>
```

**Getting the credentials:**
- **Google OAuth**: [Google Cloud Console](https://console.cloud.google.com/)
- **AWS S3**: [AWS Management Console](https://console.aws.amazon.com/)
- **Gemini API**: [Google AI Studio](https://aistudio.google.com/app/apikey)
- **MongoDB**: Provided by your database administrator

## Troubleshooting

### Python Issues

#### "python: command not found" or "Python is not installed"
- **macOS**: Install via Homebrew: `brew install python@3.11`
- **Linux**: `sudo apt install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/) (check "Add to PATH")

#### Virtual environment not activating
```bash
# macOS/Linux
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1

# Windows Command Prompt
venv\Scripts\activate
```

#### "pip: command not found"
```bash
# Use python's pip module directly
python3 -m pip install -r requirements.txt
```

#### Module import errors after `pip install`
```bash
# Ensure virtual environment is activated, then reinstall
pip install --force-reinstall -r requirements.txt
```

### Node.js / npm Issues

#### "npm: command not found"
- Reinstall Node.js from [nodejs.org](https://nodejs.org/)
- Verify installation: `npm --version`

#### npm install fails
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and package-lock.json
rm -rf node_modules package-lock.json
# Windows: rmdir /s /q node_modules & del package-lock.json

# Reinstall
npm install
```

#### Port 5173 already in use
```bash
# You can specify a different port
npm run dev -- --port 3000
```

### Django Issues

#### Django migrations fail
- Ensure MongoDB is running and credentials are correct in `.env`
- Check that `MONGODB_CLIENT_USERNAME` and `MONGODB_CLIENT_PASSWORD` are properly set
- Run migrations with more verbose output: `python manage.py migrate --verbosity 2`

#### "ModuleNotFoundError" when running Django
- Ensure virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that you're in the `backend` directory when running `manage.py`

#### Django port 8000 already in use
```bash
# Specify a different port
python manage.py runserver 8001
```

### Git Issues

#### .env file accidentally committed
If you accidentally committed your `.env` file with real credentials:

```bash
# Remove from git history
git rm --cached backend/.env
git commit --amend --no-edit
git push --force-with-lease  # Use with caution!

# Add to .gitignore if not already there
echo "backend/.env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

## Development Workflow

### Starting the Development Servers

You'll need two terminal windows/tabs:

**Terminal 1 - Backend**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python manage.py runserver
```

**Terminal 2 - Frontend**
```bash
cd frontend
npm run dev
```

### Common Development Commands

**Backend (Django)**
```bash
# Create a new Django app
python manage.py startapp app_name

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create a superuser for admin
python manage.py createsuperuser

# Access Django admin
# Visit: http://localhost:8000/admin/
```

**Frontend (React)**
```bash
# Build for production
npm run build

# Run linting
npm run lint

# Preview production build locally
npm run preview
```

## Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [MongoDB Docs](https://docs.mongodb.com/)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)

## Need Help?

If you encounter issues not covered in this guide:

1. Check the Troubleshooting section above
2. Review project-specific documentation
3. Check recent commits or issues in the repository
4. Ask your team lead or check with other developers
