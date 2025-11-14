# Django App Parameter - Demo Project

This is a demonstration project for testing `django-app-parameter` manually.

## Quick Start

### Option 1: One-Command Start (Recommended)

From the root of the `django-app-parameter` repository, run:

```bash
./demo_project/run_demo.sh
```

This will automatically:
- Set up the database if it doesn't exist (migrations, superuser, sample data)
- Start the development server at http://127.0.0.1:8000/

### Option 2: Manual Steps

**1. Setup**

From the root of the `django-app-parameter` repository, run:

```bash
./demo_project/setup_demo.sh
```

This script will:
- Remove any existing database
- Run Django migrations
- Create a superuser (username: `admin`, password: `admin`)
- Load sample parameters from fixtures

**2. Start the Development Server**

```bash
cd demo_project
python manage.py runserver
```

### Access the Application

- **Homepage**: http://127.0.0.1:8000/
  - Displays global parameters using the template context processor

- **Admin Interface**: http://127.0.0.1:8000/admin/
  - Username: `admin`
  - Password: `admin`
  - Here you can create, modify, and delete parameters

## Sample Data

The demo includes 8 pre-configured parameters:

### Global Parameters (visible in templates):
1. **Site Title**: "My Awesome Website" (STR)
2. **Contact Email**: "contact@example.com" (STR)
3. **Max Upload Size**: 10 (INT)
4. **Maintenance Mode**: false (BOOL)

### Non-Global Parameters (only accessible in Python code):
5. **Items per page**: 25 (INT)
6. **API Endpoint**: "https://api.example.com/v1" (STR)
7. **Enable notifications**: true (BOOL)
8. **Cache timeout**: 3600 (INT)

## Testing Features

### 1. Access Parameters in Templates

The homepage demonstrates accessing global parameters in templates. Try modifying them in the admin interface and refresh the homepage to see the changes instantly (no server restart needed).

### 2. Access Parameters in Python Code

Open the Django shell:

```bash
cd demo_project
python manage.py shell
```

Then test accessing parameters:

```python
from django_app_parameter import app_parameter

# Access parameters by their SLUG
print(app_parameter.SITE_TITLE)  # "My Awesome Website"
print(app_parameter.MAX_UPLOAD_SIZE)  # 10
print(app_parameter.MAINTENANCE_MODE)  # False
print(app_parameter.ITEMS_PER_PAGE)  # 25
```

### 3. Load Parameters from JSON

Try loading additional parameters:

```bash
cd demo_project
python manage.py load_param --json "[{'name': 'new param', 'value': 'test value'}]"
```

Or from a file:

```bash
python manage.py load_param --file fixtures/sample_parameters.json
```

### 4. Modify Parameters

1. Go to http://127.0.0.1:8000/admin/django_app_parameter/parameter/
2. Click on any parameter to edit it
3. Change the value and save
4. Refresh the homepage or access it in the shell to see the new value immediately

## Manual Setup (Alternative)

If you prefer to set up manually instead of using the setup script:

```bash
cd demo_project

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load sample parameters
python manage.py load_param --file fixtures/sample_parameters.json

# Start server
python manage.py runserver
```

## Clean Up

To reset the demo:

```bash
cd demo_project
rm db.sqlite3
./setup_demo.sh
```

## Project Structure

```
demo_project/
├── demo_project/
│   ├── __init__.py
│   ├── settings.py      # Django settings with django_app_parameter configured
│   ├── urls.py          # URL configuration
│   └── wsgi.py
├── fixtures/
│   └── sample_parameters.json  # Sample parameter data
├── templates/
│   └── home.html        # Demo homepage showing global parameters
├── manage.py
├── run_demo.sh          # One-command script to setup and run server
├── setup_demo.sh        # Automated setup script
└── README.md
```

## Notes

- This is a development/demo project. Do not use in production.
- The secret key is hardcoded and insecure by design.
- SQLite database is used for simplicity.
- The superuser password is intentionally weak for demo purposes.