# TGClient Update Service Backend App

## Dev environment

### Before the very first use

* If you have cloned the existing repo (not generated the repo yourself):
    ```
    # install uv
    uv sync
    uv tool run pre-commit install
    ```
* In IDE, do not forget to select the environment from `.venv`
* `docker-compose up -d --build`
* `alembic revision --autogenerate -m "Initial revision"`

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
