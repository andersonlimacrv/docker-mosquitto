import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL")
PASSWD_FILE_PATH = os.getenv("PASSWD_FILE_PATH", "./config/mosquitto.passwd")
PROJECT_ROOT = os.getenv("PROJECT_ROOT", ".")
BROKER_CN = os.getenv("BROKER_CN", "localhost")