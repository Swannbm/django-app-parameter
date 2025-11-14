#!/bin/bash
# Setup script for the demo project

set -e  # Exit on error

echo "Setting up Django App Parameter Demo Project..."
echo "=============================================="

# Navigate to demo_project directory
cd "$(dirname "$0")"

# Remove old database if exists
if [ -f "db.sqlite3" ]; then
    echo "Removing old database..."
    rm db.sqlite3
fi

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Create superuser (non-interactive)
echo "Creating superuser (admin/admin)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
EOF

# Load sample parameters
echo "Loading sample parameters..."
python manage.py load_param --file fixtures/sample_parameters.json

echo ""
echo "=============================================="
echo "Setup complete!"
echo ""
echo "To start the development server, run:"
echo "  cd demo_project"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  - Homepage: http://127.0.0.1:8000/"
echo "  - Admin: http://127.0.0.1:8000/admin/"
echo ""
echo "Admin credentials:"
echo "  Username: admin"
echo "  Password: admin"
echo "=============================================="
