#!/bin/bash
# Run script for the demo project - sets up and starts the server

set -e  # Exit on error

# Navigate to demo_project directory
cd "$(dirname "$0")"

echo "Django App Parameter - Demo Project"
echo "===================================="
echo ""

# Check if database exists
echo "Running setup..."
./setup_demo.sh

echo ""
echo "Starting development server..."
echo "=============================================="
echo "Homepage: http://127.0.0.1:8000/"
echo "Admin: http://127.0.0.1:8000/admin/"
echo ""
echo "Admin credentials:"
echo "  Username: admin"
echo "  Password: admin"
echo "=============================================="
echo ""

# Start the development server
python manage.py runserver
