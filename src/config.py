import os

from dotenv import load_dotenv

load_dotenv()

LOG_FILE_NAME: str | None = os.environ.get("LOG_FILE_NAME")
GITHUB_ORG_NAME: str | None = os.environ.get("GITHUB_ORG_NAME")
GITHUB_TOKEN: str | None = os.environ.get("GITHUB_TOKEN")