#!/bin/bash
# Run Django development server on localhost:8000

# Change to the backend directory
cd "$(dirname "$0")"

# Function to find and activate virtual environment
activate_venv() {
    # Common venv locations to check (in order of preference)
    local venv_paths=(
        "venv"
        ".venv"
        "../venv"
        "../.venv"
        "env"
        "../env"
    )

    for venv_path in "${venv_paths[@]}"; do
        if [ -f "$venv_path/bin/activate" ]; then
            echo "Found virtual environment at: $venv_path"
            source "$venv_path/bin/activate"
            return 0
        fi
    done

    echo "Warning: No virtual environment found. Using system Python."
    return 1
}

# Try to activate virtual environment
activate_venv

# Verify we have Django installed
if ! python -c "import django" 2>/dev/null; then
    echo "Error: Django is not installed in the current Python environment."
    echo "Please install requirements: pip install -r requirements.txt"
    exit 1
fi

# Run the Django development server
echo "Starting Django development server at http://localhost:8000/"
python manage.py runserver localhost:8000
