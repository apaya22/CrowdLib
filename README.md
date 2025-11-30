# CrowdLib

## Quick Start - Development Setup

### Prerequisites
- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Node.js 16+** - [Download](https://nodejs.org/)
- **npm** (comes with Node.js)

### Automated Setup
Run the initialization script to automatically set up your development environment:

```bash
bash init.sh
```

This script will:
- ✓ Check for required dependencies (Python 3, Node.js, npm)
- ✓ Create and activate a Python virtual environment
- ✓ Install Python dependencies from `requirements.txt`
- ✓ Install Node.js dependencies via npm
- ✓ Run Django migrations
- ✓ Create a `.env.example` file template

### Running the Development Servers

After setup, easily start both frontend and backend servers simultaneously:

**macOS/Linux:**
```bash
bash start_servers.sh
```

**Windows:**
```bash
start_servers.bat
```

This will automatically:
- Launch the backend Django server in one terminal (port 8000)
- Launch the frontend Vite server in another terminal (port 5173)
- Verify all dependencies are installed

See [START_SERVERS.md](START_SERVERS.md) for more details.

### Manual Setup (if not using init.sh)

#### Backend (Django)
```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env  # Edit with your actual values

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

#### Frontend (React)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Configuration

The project requires a `.env` file in the `backend/` directory. Key variables include:
- **MongoDB**: Connection credentials and database name
- **Django**: Settings module configuration
- **Google OAuth**: Client ID and secret for authentication
- **AWS S3**: Access keys and bucket configuration for image storage
- **Gemini API**: API key for AI features

See `backend/.env.example` for the complete list of required variables.

### Development Server URLs
- **Frontend**: http://localhost:5173 (Vite dev server)
- **Backend API**: http://localhost:8000 (Django development server)

### Project Structure
```
CrowdLib/
├── backend/                 # Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env                (local, not in repo)
│   └── [Django apps]
├── frontend/               # React + Vite
│   ├── package.json
│   ├── src/
│   └── [React components]
└── init.sh                 # Automated setup script
```

## Troubleshooting

### Python virtual environment issues
```bash
# Deactivate current environment
deactivate

# Recreate virtual environment
rm -rf backend/venv
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### npm install issues
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf frontend/node_modules
npm install
```

### Django migration errors
Ensure your MongoDB connection is active and credentials in `.env` are correct before running migrations.

## Additional Documentation

For more detailed information, see:
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
- [DRF Documentation](https://www.django-rest-framework.org/)