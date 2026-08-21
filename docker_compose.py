# The Setup Steps (Summary):
# Clone the repository from Git
# Create a virtual environment (python -m venv venv)
# Activate it (source venv/bin/activate)
# Install dependencies (pip install -r requirements.txt)
# Configure the .env file with database credentials
# Create the PostgreSQL database (CREATE DATABASE stroyopttorg;)
# Run migrations (python manage.py makemigrations && python manage.py migrate)
# Collect static files (python manage.py collectstatic)
# Create a superuser (python manage.py createsuperuser)
# Start Redis (in a separate terminal: redis-server)
# Run the server (python manage.py runserver)