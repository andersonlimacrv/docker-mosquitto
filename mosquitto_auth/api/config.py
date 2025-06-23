import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


API_KEY = os.getenv("API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL")
PASSWD_FILE_PATH = os.getenv("PASSWD_FILE_PATH", "./config/mosquitto.passwd")
PROJECT_ROOT = os.getenv("PROJECT_ROOT", ".")
BROKER_CN = os.getenv("BROKER_CN", "localhost")


class Settings(BaseSettings):
    # Configurações da API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # Configurações do Mosquitto
    mosquitto_host: str = "mosquitto"
    mosquitto_port: int = 8883
    mosquitto_passwd_file: str = "/app/config/mosquitto.passwd"
    
    # Configurações de certificados
    certs_dir: str = "/app/certs"
    ca_cert_path: str = "/app/certs/ca.crt"
    ca_key_path: str = "/app/certs/ca.key"
    broker_cert_path: str = "/app/certs/broker/broker.crt"
    client_certs_dir: str = "/app/certs/client"
    
    # Configurações de log
    log_dir: str = "/app/log"
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
settings = Settings()

# Funções auxiliares para paths
def get_client_cert_dir(username: str) -> Path:
    """Retorna o diretório de certificados do cliente"""
    return Path(settings.client_certs_dir) / username

def get_client_cert_path(username: str) -> Path:
    """Retorna o caminho do certificado do cliente"""
    return get_client_cert_dir(username) / f"{username}.crt"

def get_client_key_path(username: str) -> Path:
    """Retorna o caminho da chave privada do cliente"""
    return get_client_cert_dir(username) / f"{username}.key"