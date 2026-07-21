import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-relocation-advisor-key")
    WTF_CSRF_ENABLED = True
    DATA_DIR = os.path.join(BASE_DIR, "app", "data")
