import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

from app import data
from app.config import settings
from app.schemas import HealthResponse, UploadDataResponse


app = FastAPI(title="KK2 Oraklet")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/data/upload", response_model=UploadDataResponse)
async def upload_data(file: UploadFile = File(...)) -> UploadDataResponse:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    content = await file.read()
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(status_code=400, detail="CSV file is too large")

    try:
        df = data.save_csv(content)
    except pd.errors.EmptyDataError as exc:
        raise HTTPException(status_code=400, detail="CSV file is empty") from exc
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV file has invalid encoding") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadDataResponse(
        rows=len(df),
        columns=list(df.columns),
        dtypes={column: str(dtype) for column, dtype in df.dtypes.items()},
    )
