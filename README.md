# TGClient Update Service Backend App

## Dev environment

### Before the very first use

* ```
    # install uv
    uv sync
    uv tool run pre-commit install
    ```
* In IDE, do not forget to select the environment from `.venv`

### Setting application parameters
* Copy .env.example to .env
* Set the following variables:
    * app_api_key
    * app_crm_url_base - CRM or mock URL not including '/1/validate-token'

### Running the application (non-containerized)
`python -m app`

### Running the application (Docker)
`docker compose up -d --build`

### Running tests
1. Run `docker compose up` to launch a local PostgreSQL instance
2. Make sure the database `autotest` exists (create if necessary)
3. Run `pytest` and make sure all tests are passing

### Running linters
* `ruff check`
* `mypy app`

# Deployment

## Linting and unit testing

* `docker build --tag app-update-service-test --target test .`
* `docker run --rm app-update-service-test ruff check`
* `docker run --rm app-update-service-test mypy app`
* `docker run --rm app-update-service-test pytest tests/unit`

## Building

* `docker build --tag app-update-service .`

## Running

* Obtain PosgreSQL connection parameters: host, port, user, password, DB name
* Arrange file storage for update files with access for uid=1000 gid=1000
    * `sudo chown 1000:1000 /path/to/file_storage`
* Arrange file storage for log files with access for uid=1000 gid=1000
    * `sudo chown 1000:1000 /path/to/log_storage`
* Prepare environment variables:
    * app_host - bind application socket to this host
    * app_port - bind application socket to this port
    * postgres_host
    * postgres_port
    * postgres_user
    * postgres_password
    * postgres_db - DB name
    * app_api_key - key for accessing API service endpoints (normally one would just generate a new secure key)
    * app_crm_url_base - base URL of CRM (not including /1/validate-token)
    * logger_file_max_size - rotate log file on this size, bytes, default 0 (rotation is off)
    * logger_file_backup_count - keep this number of old log files during rotation, default 0 (rotation is off)
* Run database mirgations passing environment variables:
    * `docker run --env-file .env --rm app-update-service bash -c "alembic upgrade head"`
* Run the application passing environment variables and mounting the two file storages to container's `/persistent/file_storage` and `/persistent/log_storage`:
    * `docker run -d --env-file .env -p 8080:8080 -v /path/to/file_storage:/persistent/file_storage -v /path/to/log_storage:/persistent/log_storage app-update-service`
* For a docker compose example, see docker-compose-deploy-example.yml
