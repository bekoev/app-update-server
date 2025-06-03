FROM python:3.12-slim AS build

WORKDIR /tmp
RUN pip install uv
COPY pyproject.toml uv.lock /tmp/
RUN uv export --no-dev --format requirements-txt > requirements.txt
RUN uv export --format requirements-txt > dev-requirements.txt


FROM python:3.12-slim AS test

RUN mkdir /persistent && mkdir /persistent/log_storage
WORKDIR /backend
COPY --from=build /tmp/dev-requirements.txt /backend/dev-requirements.txt
RUN pip install --no-cache-dir --upgrade -r /backend/dev-requirements.txt
COPY ./app /backend/app
COPY ./tests /backend/tests
COPY ./pytest.ini /backend/


FROM python:3.12-slim

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN addgroup --gid $GROUP_ID nonroot && adduser --uid $USER_ID --ingroup nonroot nonroot
RUN mkdir /persistent && mkdir /persistent/file_storage && chown -R nonroot:nonroot /persistent/file_storage
RUN mkdir /persistent/log_storage && chown -R nonroot:nonroot /persistent/log_storage

WORKDIR /backend

COPY --from=build /tmp/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt
COPY ./alembic.ini /backend/
COPY ./migrations /backend/migrations
COPY ./app /backend/app

USER nonroot

CMD ["python", "-m", "app"]
