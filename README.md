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
* Set the app_api_key variable to the value corresponging to api_token from TGClient's settings.ini (excluding the "Bearer " prefix).

### Running the application (non-containerized)
`python -m app`

### Running the application (Docker)
`docker-compose up -d --build`

### Running tests
1. Run `docker compose up` to launch a local PostgreSQL instance
1. Make sure the database `autotest` exists (create if necessary)
1. Run `pytest` and make sure all tests are passing


### Running linters
`ruff check`
`mypy app`
