# DrugCentral2020

DrugCentral provides information on active ingredients chemical entities, pharmaceutical products, drug mode of action, indications, pharmacologic action. We monitor FDA, EMA, and PMDA for new drug approval on regular basis to ensure currency of the resource. Limited information on discontinued and drugs approved outside US is also available however regulatory approval information can't be verified.

# Database Initialization
The database is automatically initialized with:

PostgreSQL 14

RDKit extension

Preloaded drugcen.dump data

The Dockerfile.db handles RDKit compilation, PostgreSQL setup, and extension creation.

# Instructions to run Drugcentral App locally
1. Install docker & docker compose
2. Clone the repository
3. cd drugcen
4. run this in terminal `docker-compose --env-file .env -f compose.yml up --build`
5. listening at http://localhost:8000

<h2>Authors</h2>
<div id="async-workers">

Oleg Ursu, Jayme Holmes, Cristian G Bologa, Jeremy J Yang, Stephen L Mathias, Vasileios Stathias, Dac-Trung Nguyen, Stephan Schürer, Tudor Oprea </div>

# License

DrugCentral is available under <a href="https://creativecommons.org/licenses/by-sa/4.0/legalcode" target="_blank">Creative Commons license</a>,<br>
download and use of this resource evidences your agreement to all the terms and conditions of license.
