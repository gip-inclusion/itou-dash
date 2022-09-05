import os
from pathlib import Path

from dotenv import load_dotenv

ENV = os.environ.get("ENV")

DOTENV = Path(__file__).parent / "environments" / ".env"
load_dotenv(DOTENV)

DATA_PATH = Path(__file__).parent / "data"
