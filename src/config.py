import os
import sys

from dotenv import load_dotenv

basedir: str
if getattr(sys, "frozen", False):
    basedir = os.path.dirname(sys.executable)
else:
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv_path: str = os.path.join(basedir, ".env")

load_dotenv(dotenv_path=dotenv_path, override=True)

LOG_FILE_PATH: str | None = os.getenv("LOG_FILE_PATH")
DESTINATION_FOLDER_NAME: str | None = os.getenv("DESTINATION_FOLDER_NAME")