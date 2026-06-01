from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class UploadDataResponse(BaseModel):
    rows: int
    columns: list[str]
    dtypes: dict[str, str]
