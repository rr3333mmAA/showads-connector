from typing import cast

from fastapi import Depends, FastAPI
from pydantic import BaseModel

from .models import AgeLimit

app = FastAPI()
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
