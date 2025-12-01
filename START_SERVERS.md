# CrowdLib Master Start Servers Script

Quick and easy way to start both the frontend and backend development servers simultaneously.

## Disclosure: This document was AI Generated

## Overview

The master start server scripts automatically launch both servers in separate terminal windows. No need to manually open terminals and run commands - just run one script!

### Available Scripts

- **macOS/Linux**: `start_servers.sh`
- **Windows**: `start_servers.bat`

## Prerequisites

Before using these scripts, ensure:
1. You have run the initialization script (`init.sh` or `init.bat`)
2. Backend virtual environment is set up
3. Frontend dependencies are installed
4. Backend `run_server.sh` exists

## Quick Start

### macOS/Linux

```bash
bash start_servers.sh
```

This will:
- Verify all prerequisites
- Open a new Terminal window for the backend server
- Open another new Terminal window for the frontend server
- Display the server URLs

### Windows

```bash
start_servers.bat
```

Or simply double-click `start_servers.bat` in File Explorer.

This will:
- Verify all prerequisites
- Open a new Command Prompt window for the backend server
- Open another new Command Prompt window for the frontend server
- Display the server URLs

## What It Does

### Checks
The script performs the following validation checks before starting servers:

1. ✓ Verifies backend `run_server.sh` exists
2. ✓ Confirms frontend directory exists
3. ✓ Checks frontend dependencies are installed
4. ✓ Confirms backend virtual environment exists

### Starts Servers
Once all checks pass, it:

1. **Backend Server** - Runs the existing `backend/run_server.sh` script
   - Activates Python virtual environment
   - Starts Django development server
   - Available at: `http://localhost:8000`

2. **Frontend Server** - Runs `npm run dev` in the frontend directory
   - Starts Vite development server
   - Available at: `http://localhost:5173` (typically)

## Server URLs

After running the script, access your application at:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin/

## Stopping the Servers

To stop the servers, you have two options:

### Option 1: Close Terminal Windows
Simply close the terminal windows where the servers are running.

### Option 2: Keyboard Shortcut
In each terminal window, press:
- **Ctrl+C** (macOS/Linux/Windows)

Both servers will shut down gracefully.

## Troubleshooting

### Script Says Prerequisites Not Met

#### Backend run_server.sh not found
```bash
# Make sure you're in the project root directory
# The script should be at: backend/run_server.sh
```

#### Frontend dependencies not installed
```bash
cd frontend
npm install
```

#### Virtual environment not found
```bash
# Run initialization script
bash init.sh  # macOS/Linux
init.bat      # Windows
```

### Terminal Windows Don't Open

#### macOS
- Ensure Terminal app is installed (standard on all Macs)
- Try running directly in an existing terminal instead:
  ```bash
  cd backend && bash run_server.sh &
  cd frontend && npm run dev
  ```

#### Linux
The script supports:
- GNOME Terminal (most common)
- Konsole (KDE)
- xterm (fallback)

If none are available, run servers manually:
```bash
# Terminal 1
cd backend && bash run_server.sh

# Terminal 2
cd frontend && npm run dev
```

#### Windows
- Ensure bash is available (Git Bash or WSL)
- The script opens Command Prompt windows automatically
- If `npm` or `bash` commands don't work, check that Node.js is in your PATH

### Port Already in Use

If you get an error about ports being in use:

#### Port 8000 (Backend) is in use
```bash
# Run on a different port
cd backend
source venv/bin/activate
python manage.py runserver 8001
```

#### Port 5173 (Frontend) is in use
```bash
# Run on a different port
cd frontend
npm run dev -- --port 3000
```

### Backend Server Won't Start

Check the backend terminal window for error messages:

1. **Django not installed**
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Database connection issues**
   - Check `.env` file has correct MongoDB credentials
   - Ensure MongoDB server is running

3. **Migrations needed**
   ```bash
   cd backend
   source venv/bin/activate
   python manage.py migrate
   ```

### Frontend Server Won't Start

Check the frontend terminal window for error messages:

1. **npm modules missing**
   ```bash
   cd frontend
   npm install
   ```

2. **Node version issue**
   ```bash
   node --version  # Should be 16+
   npm --version   # Should be 7+
   ```

## Manual Server Start (Alternative)

If you prefer to start servers manually or the scripts don't work:

### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
bash run_server.sh
```

Or directly:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

## Advanced Usage

### Custom Ports

To use different ports, modify the server startup commands:

#### Backend
Edit `backend/run_server.sh` or run:
```bash
python manage.py runserver 8001
```

#### Frontend
```bash
npm run dev -- --port 3000
```

### Environment Variables

If you need to set environment variables before starting:

#### macOS/Linux
```bash
export VARIABLE_NAME=value
bash start_servers.sh
```

#### Windows
```cmd
set VARIABLE_NAME=value
start_servers.bat
```

### Debugging

To see more detailed output:

#### macOS/Linux
```bash
bash -x start_servers.sh
```

#### Windows
Edit `start_servers.bat` and add:
```batch
@echo on
```

## Integration with Development Workflow

### During Development
1. Run `bash start_servers.sh` to start both servers
2. Open `http://localhost:5173` in your browser
3. Make code changes - servers auto-reload (with hot module replacement)
4. Check terminal windows for any error messages
5. Close terminal windows when done developing

### With Version Control
Don't commit the terminal window state - the scripts are designed to be run fresh each time.

## Notes

- The scripts will fail gracefully if prerequisites aren't met
- Both servers log to their respective terminal windows
- Close windows in any order - stopping one server doesn't affect the other
- The frontend server typically includes hot module reload (HMR) - changes show immediately
- The backend server will auto-reload Python file changes (Django development server feature)

## See Also

- [README.md](README.md) - Main project documentation
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions
- [QUICK_START.md](QUICK_START.md) - Quick reference guide
- [backend/run_server.sh](backend/run_server.sh) - Backend startup script

## Customization

To modify the scripts for your needs:

1. **Change port numbers**: Edit the `python manage.py runserver` command
2. **Add environment variables**: Source a `.env` file before starting servers
3. **Add additional startup tasks**: Add commands to check database, run migrations, etc.
4. **Customize output**: Modify the echo statements for different formatting

---

For issues or improvements, refer to the main documentation or check with your team lead.
