from fastapi import HTTPException, status


class ApiNotFoundError(HTTPException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "not found"


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


class ApiUnauthorizedError(HTTPException):
    def __init__(self, message: str | None = None):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = message if message else "unauthorized"
