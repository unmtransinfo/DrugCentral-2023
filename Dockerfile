FROM python:3.12-alpine

# Install system dependencies
RUN apk update && \
    apk add --no-cache \
        curl \
        netcat-openbsd \
        gcc \
        libpq-dev \
        postgresql-client \
        freetype-dev


# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
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
