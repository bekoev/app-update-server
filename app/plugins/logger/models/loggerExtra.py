from pydantic import BaseModel

from app.plugins.logger.enums.loggerOperationType import LoggerOperationType


class LoggerExtra(BaseModel):
    operation_type: LoggerOperationType | None = None
    entity_type: str | None = None
    task_name: str | None = None
    changes_in_model: dict | None = None

    @classmethod
    def get_extra_fields(cls):
        return cls.model_fields
