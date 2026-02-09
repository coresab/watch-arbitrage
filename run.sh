#!/bin/bash

# Watch Arbitrage - Local Development Setup

echo "=== Watch Arbitrage Setup ==="

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo ">>> Please edit .env with your API credentials <<<"
fi

# Initialize database and seed data
echo "Initializing database..."
python -c "from models import init_db; init_db()"

echo "Seeding watch catalog..."
python seed_data.py

# Run the app
echo ""
echo "=== Starting Dashboard ==="
echo "Open http://localhost:8050 in your browser"
echo ""
python app.py
