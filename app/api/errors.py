from fastapi import HTTPException, status

# TODO Remove Error-s that are unnecessary in the boilerplate


class ApiNotFoundError(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "not found"


class ApiExistsError(HTTPException):
    def __init__(self, message: str | None = None):
        self.status_code = status.HTTP_409_CONFLICT
        self.detail = message if message else "already exists"


class ApiTechnicalError(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        self.detail = "internal server error"


class WrongDataError(HTTPException):
    def __init__(self, loc="unk", message="field required"):
        self.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        self.loc = loc
        self.detail = [
            {
                "loc": (self.loc,),
                "msg": message,
                "type": "value_error",
            },
        ]


class EntityNotFound(HTTPException):
    def __init__(self, entity_name: str | None = None):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = f"Entity{' ' + entity_name if entity_name else ''} not found"
        self.entity = entity_name


class MissDataError(WrongDataError):
    def __init__(self, loc):
        super().__init__(loc=loc)
