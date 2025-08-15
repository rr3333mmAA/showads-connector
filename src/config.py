import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Configuration loaded from environment variables.
    """
    api_base_url: str
    project_key: str

    @classmethod
    def load(cls) -> "Config":
        api_base_url = os.getenv("SHOWADS_BASE_URL")

        if not api_base_url:
            raise ValueError("SHOWADS_BASE_URL is not set in the environment variables")

        return cls(
            api_base_url=api_base_url,
            project_key=os.getenv("SHOWADS_PROJECT_KEY", "dev-key")
        )