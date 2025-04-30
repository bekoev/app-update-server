from pydantic import BaseModel


class UpdateManifest(BaseModel):
    version: str
    url: str
