# DrugCentral 2023

DrugCentral is a comprehensive, open-access database that integrates information on active chemical entities, pharmaceutical products, drug modes of action, indications, and pharmacologic actions. It is maintained by monitoring major regulatory bodies (FDA, EMA, and PMDA) for new drug approvals on a regular basis.

## Key Features

-   **Comprehensive Drug Data**: Detailed information on drug ingredients, formulations, and regulatory history.
-   **Full-Text Search**: Robust search capabilities across drug names, synonyms, and approval statuses.
-   **Cheminformatics Support**: Advanced substructure and similarity searching powered by the **RDKit** PostgreSQL extension.
-   **Regulatory Tracking**: Dedicated monitoring of FDA (US), EMA (Europe), and PMDA (Japan) approvals.
-   **Data Export**: Access to underlying datasets for research and analysis.

## Technical Architecture

### Backend Stack
-   **Django 3.2.24**: The core web framework (running on Python 3.12).
-   **Gunicorn**: Production-grade WSGI HTTP server.
-   **Whitenoise**: Efficient serving of static assets directly from the application.

### Database Architecture
-   **PostgreSQL 14**: The primary data store.
-   **RDKit PostgreSQL Extension**: Compiled from source to enable advanced molecular search capabilities (`m@>` for substructure and `mfp2%morganbv_fp` for similarity).
-   **Custom Build**: The database image is built from `Dockerfile.db`, which installs the necessary build tools and libraries (Boost, Eigen, etc.) to compile RDKit.

### Infrastructure & Deployment
-   **Docker & Docker Compose**: Used for both local development and production orchestration.
-   **Nginx Proxy**: Handles reverse proxying, static file serving, and SSL termination.
-   **Certbot**: Automates SSL certificate management via Let's Encrypt.

## Setup and Local Development

### Prerequisites
-   Docker and Docker Compose (V2+)
-   At least 4GB of RAM (for RDKit compilation)

### Initial Configuration
1.  **Clone the repository**:
    ```bash
    git clone https://github.com/unmtransinfo/DrugCentral-2023.git
    cd DrugCentral-2023
    ```
2.  **Environment Variables**: Create a `.env` file based on `.env.example`:
    ```bash
    cp .env.example .env
    ```
    *Ensure you configure your `POSTGRES_PASSWORD` and other credentials.*

### Running Locally
1.  **Start the services**:
    ```bash
    docker compose up --build
    ```
    *Note: The first build of the database service will take 10-15 minutes as it compiles RDKit and installs dependencies.*

2.  **Access the application**:
    Open [http://localhost:8000](http://localhost:8000) in your browser.

## CI/CD Pipeline

The project uses GitHub Actions (`.github/workflows/docker-publish.yml`) to manage the container lifecycle:
-   **Automatic Builds**: Every push to the `main` branch triggers a build of the `web` and `nginx` images.
-   **DockerHub Integration**: Images are automatically pushed to the `unmtransinfo` organization on DockerHub.

> [!IMPORTANT]
> Because of the large size of the database dump (`init/drugcen.dump`) and the time required to compile RDKit, the **Database image** must be built and pushed manually when changes are made locally.

Manual database update:
```bash
docker compose build db
docker compose push db
```

## Production Deployment (AWS)

The production environment is orchestrated via `compose.prod.yml`. It handles Nginx configuration, Certbot SSL automation, and production-ready environment variables.

### Update Production
To deploy the latest images to production:
1.  SSH into your EC2 instance.
2.  Pull the latest images from DockerHub:
    ```bash
    docker compose -f compose.prod.yml pull
    ```
3.  Restart the application in detached mode:
    ```bash
    docker compose -f compose.prod.yml up -d
    ```

## Authors
**Oleg Ursu, Jayme Holmes, Cristian G Bologa, Jeremy J Yang, Stephen L Mathias, Vasileios Stathias, Dac-Trung Nguyen, Stephan Schürer, Tudor Oprea**

*University of New Mexico, Translational Informatics Division*

## License
DrugCentral is available under the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/legalcode). Download and use of this resource evidences your agreement to all the terms and conditions of the license.
