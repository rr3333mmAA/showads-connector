import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Configuration loaded from environment variables.
    """
    api_base_url: str
    project_key: str
    min_banner_id: int
    max_banner_id: int
    token_expiry_seconds: int
    max_retries: int
    retry_backoff_seconds: int
    bulk_batch_size: int
    
    @classmethod
    def load(cls) -> "Config":
        api_base_url = os.getenv("SHOWADS_BASE_URL")

        if not api_base_url:
            raise ValueError("SHOWADS_BASE_URL is not set in the environment variables")

        return cls(
            api_base_url=api_base_url,
            project_key=os.getenv("SHOWADS_PROJECT_KEY", "dev-key"),
            min_banner_id=int(os.getenv("MIN_BANNER_ID", "1")),
            max_banner_id=int(os.getenv("MAX_BANNER_ID", "99")),
            token_expiry_seconds=int(os.getenv("TOKEN_EXPIRY_SECONDS", "84600")),  # 23.5 hours in seconds
            max_retries=int(os.getenv("MAX_RETRIES", "5")),
            retry_backoff_seconds=int(os.getenv("RETRY_BACKOFF_SECONDS", "2")),
            bulk_batch_size=int(os.getenv("BULK_BATCH_SIZE", "1000")),
        )
