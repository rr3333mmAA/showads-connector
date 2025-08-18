import os
import shutil
from tempfile import NamedTemporaryFile
from typing import Optional, cast

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from .config import Config
from .logger import setup_logging
from .models import AgeLimit
from .processor import process_csv
from .showads_client import ShowAdsClient

app = FastAPI()
setup_logging()
config = Config.load()
app.state.age_limit = AgeLimit()

class AgeLimitPayload(BaseModel):  # type: ignore
    min_age: int
    max_age: int

def get_age_limit() -> AgeLimit:
    return cast(AgeLimit, app.state.age_limit)

@app.get("/health")  # type: ignore
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/config/age-limit")  # type: ignore
def get_age_limit(age_limit: AgeLimit = Depends(get_age_limit)) -> AgeLimit:
    return age_limit

@app.put("/config/age-limit")  # type: ignore
def set_age_limit(payload: AgeLimitPayload) -> AgeLimit:
    age_limit = AgeLimit(min_age=payload.min_age, max_age=payload.max_age)
    app.state.age_limit = age_limit
    return age_limit

@app.post("/process/csv")  # type: ignore
async def upload_csv(
    file: UploadFile = File(...),
    age_limit: AgeLimit = Depends(get_age_limit),
) -> dict[str, str | int]:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")

    client = ShowAdsClient(config)

    tmp_path: Optional[str] = None
    try:
        with NamedTemporaryFile(mode="wb", delete=False, suffix=".csv") as tmp:
            tmp_path = tmp.name
            await file.seek(0)
            shutil.copyfileobj(file.file, tmp)

        valid_customers, invalid_customers = process_csv(tmp_path, config, age_limit, client)
        return {"status": "processed", "valid_customers": valid_customers, "invalid_customers": invalid_customers}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process CSV")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
