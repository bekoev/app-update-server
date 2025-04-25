FROM python:3.12-slim AS build

WORKDIR /tmp
# TODO: Align with https://docs.astral.sh/uv/guides/integration/docker/
RUN pip install uv
COPY pyproject.toml uv.lock /tmp/
RUN uv export --no-dev --format requirements-txt > requirements.txt
RUN uv export --format requirements-txt > dev-requirements.txt


FROM python:3.12-slim AS test

WORKDIR /backend
COPY --from=build /tmp/dev-requirements.txt /backend/dev-requirements.txt
RUN pip install --no-cache-dir --upgrade -r /backend/dev-requirements.txt
COPY ./app /backend/app
COPY ./tests /backend/tests
COPY ./pytest.ini ./setup.cfg /backend/


FROM python:3.12-slim

# ARG APP_VERSION=unspecified

WORKDIR /backend
COPY --from=build /tmp/requirements.txt /backend/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /backend/requirements.txt
COPY ./app /backend/app
# RUN echo "version = \"$APP_VERSION\"" > /backend/app/version.py

RUN useradd nonroot
RUN mkdir pgp_tmp && chown -R nonroot:nonroot /backend/pgp_tmp
USER nonroot
CMD ["python", "-m", "app"]
