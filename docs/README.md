# DrugCentral AWS Infrastructure & Deployment Guide

This document provides detailed internal documentation for the DrugCentral 2023 infrastructure on AWS.

## 1. Environment Overview

-   **Primary Domain:** [https://drugcentral.org](https://drugcentral.org)
-   **Service:** Amazon EC2 (Elastic Compute Cloud)
-   **Instance Type:** `t3.medium` (2 vCPU, 4 GB RAM)
-   **Operating System:** Amazon Linux 2023 (AL2023)
-   **Global User/Org (DockerHub):** `unmtransinfo`

## 2. Server Configuration

### Docker Installation (AL2023)
Amazon Linux 2023 uses `dnf` for package management:
```bash
sudo dnf update -y
sudo dnf install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user
```

### Docker Compose
Install the Docker Compose plugin:
```bash
sudo dnf install -y docker-compose-plugin
```
*Verify:* `docker compose version`

## 3. Deployment Architecture

The application is containerized and orchestrated via Docker Compose, using shared volumes for data persistence and synchronization.

### Image Registry
Images are hosted on DockerHub under the `unmtransinfo` organization.

| Image Name | Purpose |
| :--- | :--- |
| `unmtransinfo/drugcen-db:latest` | PostgreSQL 14 + RDKit Cheminformatics Extension |
| `unmtransinfo/drugcen-web:latest` | Django application backend |
| `unmtransinfo/drugcen-nginx:latest` | Nginx reverse proxy + SSL termination |

### Volume Management
-   `pgdata`: Persistent storage for the PostgreSQL database (`/var/lib/postgresql/data`).
-   `static_volume`: A shared named volume between `web` and `nginx` to ensure CSS/JS/Images are correctly synchronized.

## 4. Operational Workflows

### Standard Deployment
Always use `compose.prod.yml` on the production server.

```bash
docker compose -f compose.prod.yml pull
docker compose -f compose.prod.yml up -d
```

### Clearing "Caching" Issues
If changes in the code or static assets are not showing up on the live site, force a container recreation:
```bash
# 1. Pull the absolute latest images
docker compose -f compose.prod.yml pull

# 2. Force container recreation and clear stale states
docker compose -f compose.prod.yml up -d --force-recreate

# 3. Clean up dangling images to free up disk space
docker image prune -af
```

### SSL Management (Certbot)
SSL is managed via Certbot. The certificates are stored in `./nginx/certbot/conf` and mounted into the Nginx container.

To renew certificates:
```bash
docker compose -f compose.prod.yml run --rm certbot renew
```

## 5. Security & Maintenance

### Firewall Settings (EC2 Security Group)
-   **SSH (22)**: Management access.
-   **HTTP (80)**: Redirected to HTTPS.
-   **HTTPS (443)**: Primary application traffic.

### Application Settings
In production, `DEBUG` is set to `False` in `drugcen/settings.py` for security. Ensure `ALLOWED_HOSTS` includes `drugcentral.org`.

## 6. CI/CD Integration

### GitHub Actions
The `.github/workflows/docker-publish.yml` workflow automatically rebuilds and pushes the `web` and `nginx` images on every push to the `main` branch.

### Manual DB Updates
The `db` image contains the compiled RDKit extension and the initial data dump (`init/drugcen.dump`). It is **NOT** built automatically in CI/CD due to its size and build time. Update it manually if the schema changes:
```bash
docker compose build db
docker compose push db
```