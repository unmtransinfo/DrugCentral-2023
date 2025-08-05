# DrugCentral AWS Configuration Documentation

## 1. EC2 Instance Configuration

- **Service Used:** Amazon EC2 (Elastic Compute Cloud)
- **Instance Type:** t3.medium (2 vCPU, 4 GB RAM)
- **AMI:** Amazon Linux 2023
- **Storage:**
  - Root EBS volume: Extended to 20 GB to accommodate ~10 GB of Docker images and container data.
- **Networking:**
  - Security Group allows:
    - SSH: Port 22
    - HTTP: Port 80
    - HTTPS: Port 443
    - Application: Port 8000
- **Elastic IP:** No Elastic IP assigned
- **Hostname/IP:** [http://3.14.79.108:8000](http://3.14.79.108:8000)

## 2. Docker and Docker Compose

### Docker Installation
```bash
sudo yum update -y
sudo amazon-linux-extras enable docker
sudo yum install -y docker
sudo service docker start
sudo usermod -aG docker ec2-user
```

### Docker Compose v2 Plugin
```bash
mkdir -p ~/.docker/cli-plugins/
curl -SL https://github.com/docker/compose/releases/download/v2.27.1/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
chmod +x ~/.docker/cli-plugins/docker-compose
```

**Verify Installation:**
```bash
docker compose version
```

## 3. Docker Images Used

All images are prebuilt and hosted on DockerHub under [https://hub.docker.com/u/bspanthi](https://hub.docker.com/u/bspanthi).

| Image Name                | Purpose              |
|---------------------------|----------------------|
| bspanthi/drugcen-db       | PostgreSQL + Schema  |
| bspanthi/drugcen-web      | Django Backend       |
| bspanthi/drugcen-nginx    | Nginx Reverse Proxy  |

**Image Pull Example:**
```bash
docker pull bspanthi/drugcen-db
docker pull bspanthi/drugcen-web
docker pull bspanthi/drugcen-nginx
```

## 4. Application Deployment (Docker Compose)

The application is orchestrated using Docker Compose:
```bash
docker compose -f docker-compose.prod.yml up -d
```

### Environment Variables
- Built directly into Docker images using ENV directives.
- `.env` file is required during runtime due to internalized configuration.
- PostgreSQL credentials, DB names, and other secrets should be included within the `.env` before build step.

## 5. Nginx and Reverse Proxy

- **Container:** bspanthi/drugcen-nginx ([DockerHub link](https://hub.docker.com/u/bspanthi))
- **Purpose:** Forwards external HTTP traffic to Django app on port 8000.
- **Host Binding:**
  - External Port 80 → Internal drugcen-web:8000
- **Future work:** Enable SSL via Let's Encrypt (Certbot) when domain is routed.

## 6. PostgreSQL Database

- Runs as a separate container via `drugcen-db` image.
- Uses a volume for data persistence: `/var/lib/postgresql/data`.
- Exposed only internally within Docker network; not publicly accessible.

## 7. Testing and Verification

Verified via: [http://3.14.79.108:8000](http://3.14.79.108:8000)

API and UI tested for:
- Page load
- Backend database connection
- Basic search queries
- Static files through Nginx

## 8. Domain Transfer Plan

- **Current domain:** drugcentral.org (hosted on DigitalOcean DNS)
- **Planned migration:**
  - Transfer DNS zone to AWS Route 53
  - Create a hosted zone for drugcentral.org
  - Update name servers at domain registrar to point to Route 53
  - Map A record to EC2 Elastic IP
  - Add SSL via Certbot + Nginx

---
[http://3.14.79.108:8000/](http://3.14.79.108:8000/)