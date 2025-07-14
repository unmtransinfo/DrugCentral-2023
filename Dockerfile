FROM python:3.10.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        netcat-openbsd \
        gcc \
        libpq-dev \
        postgresql-client \
        libfreetype6-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Set environment variables (important for Django settings)
ENV DJANGO_SETTINGS_MODULE=drugcen.settings
ENV DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Make runserver script executable
RUN chmod +x ./runserver.sh

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start app
CMD ["./runserver.sh"]
