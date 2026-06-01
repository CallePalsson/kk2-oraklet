import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    model_name: str = os.getenv(
        "MODEL_NAME",
        "HuggingFaceTB/SmolLM2-135M-Instruct",
    )
    max_upload_bytes: int = int(os.getenv("MAX_UPLOAD_BYTES", "1000000"))


settings = Settings()
