from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # ⚙️ API Settings
    API_PORT: int = 8000
    API_KEY: str
    api_host: str = "0.0.0.0"
    api_debug: bool = True
    log_level: str = "INFO"
    
    # 🪰 Mosquitto Settings
    BROKER_CN: str
    BROKER_PORT: int = 8883
    PASSWD_FILE_PATH: Path = Path("./config/mosquitto.passwd")
    
    # 🔐 CERTS
    certs_dir: Path = "certs"
    ca_cert_path: Path = "certs/ca.crt"
    ca_key_path: Path = "certs/ca.key"
    broker_cert_path: Path = "certs/broker/broker.crt"
    broker_key_path: Path = "certs/broker/broker.key"
    broker_dir: Path = "certs/broker"
    client_certs_dir: Path = "certs/client"
    
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="allow"
    )

settings = Settings()


