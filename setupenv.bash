#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create virtual environment
echo -e "${BLUE}Creating Python virtual environment...${NC}"
python3 -m venv venv

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install django
pip install djangorestframework
pip install python-dotenv
pip install django-cors-headers

# Create requirements.txt for future use
pip freeze > requirements.txt

echo -e "${GREEN}✓ Setup complete!${NC}"
echo -e "${GREEN}✓ Virtual environment created and dependencies installed${NC}"
echo -e "${BLUE}To activate the environment in the future, run:${NC}"
echo "source venv/bin/activate"
