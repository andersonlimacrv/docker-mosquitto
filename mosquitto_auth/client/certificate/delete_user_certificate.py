from pathlib import Path
import shutil
from mosquitto_auth.api.core.config import settings

CERTS_BASE_DIR = settings.client_certs_dir

def delete_user_certificate(username: str):
    cert_dir = CERTS_BASE_DIR / username
    if not cert_dir.exists() or not cert_dir.is_dir():
        raise FileNotFoundError(f"Certificate directory for user '{username}' not found.")
    try:
        shutil.rmtree(cert_dir)
    except Exception as e:
        raise RuntimeError(f"Error removing user certificate: {e}") 