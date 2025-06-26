import os

from dotenv import load_dotenv

load_dotenv()

LOG_FILE_NAME: str | None = os.environ.get("LOG_FILE_NAME")