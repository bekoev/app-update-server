from datetime import timedelta
from functools import partial
from time import time
from typing import Iterable, Optional

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, Field, RootModel

from app.plugins.base.plugin import Plugin
from app.routers.auth_validation import check_access_by_api_key


class RootResponseSchema(BaseModel):
    name: str
    version: Optional[str] = None


class PingResponseSchema(RootModel):
    root: str = "pong"


class HealthcheckCallSchema(BaseModel):
    passed: bool
    elapsed: timedelta


class HealthcheckResponseSchema(BaseModel):
    healthy: bool = True
    checks: dict[str, HealthcheckCallSchema] = Field(default_factory=dict)


async def call_health_check(
    health_checks: Iterable[Plugin], background_tasks: BackgroundTasks
) -> HealthcheckResponseSchema:
    response = HealthcheckResponseSchema()
    for plugin in health_checks:
        started_at = time()
        passed = await plugin.health_check_call()
        finished_at = time() - started_at
        elapsed_time = timedelta(seconds=finished_at)

        if not passed:
            # logger.error(f"HealthCheck {plugin.healthcheck_name} failed")
            response.healthy = False

        response.checks[plugin.healthcheck_name] = HealthcheckCallSchema(
            passed=passed, elapsed=elapsed_time
        )
    return response


def create_health_router(
    title: str,
    version: Optional[str],
    health_checks: Iterable[Plugin],
) -> APIRouter:
    router = APIRouter(tags=["health-checks"])
    router.add_api_route(
        "/info",
        endpoint=lambda: RootResponseSchema(name=title, version=version),
        summary="General service information",
        response_model=RootResponseSchema,
        operation_id="app_info",
        dependencies=[Depends(check_access_by_api_key)],
    )
    router.add_api_route(
        "/ping",
        endpoint=lambda: PingResponseSchema(),
        summary='"Pong" response',
        response_model=PingResponseSchema,
        operation_id="app_ping",
        dependencies=[Depends(check_access_by_api_key)],
    )
    router.add_api_route(
        "/health",
        endpoint=partial(call_health_check, health_checks),
        summary="Call health checks",
        response_model=HealthcheckResponseSchema,
        operation_id="app_health",
        dependencies=[Depends(check_access_by_api_key)],
    )
    return router
