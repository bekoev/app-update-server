from pydantic import BaseModel


class UpdateManifest(BaseModel):
    version: str
    file_name: str
