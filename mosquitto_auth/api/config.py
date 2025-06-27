from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ⚙️ API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = True
    log_level: str = "INFO"
    API_KEY: str
    
    # 🪰 Mosquitto Settings
    BROKER_CN: str
    BROKER_PORT: int = 8883
    PASSWD_FILE_PATH: Path = Path("./config/mosquitto.passwd")
    
    # 🔐 CERTS
    certs_dir: str = "/app/certs"
    ca_cert_path: str = "/app/certs/ca.crt"
    ca_key_path: str = "/app/certs/ca.key"
    broker_cert_path: str = "/app/certs/broker/broker.crt"
    client_certs_dir: str = "/app/certs/client"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="allow"
    )

settings = Settings()


