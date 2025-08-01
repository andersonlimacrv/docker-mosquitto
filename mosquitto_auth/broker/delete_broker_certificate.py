from pathlib import Path
from mosquitto_auth.api.core.config import settings

def delete_broker_certificate():
    base_dir = Path(__file__).parent.parent.parent
    print(base_dir)
    broker_cert = base_dir / settings.broker_cert_path
    print(broker_cert)
    broker_key = base_dir / settings.broker_key_path
    print(broker_key)
    
    removed = False
    for f in [broker_cert, broker_key]:
        if f.exists():
            f.unlink()
            removed = True
    if not removed:
        raise FileNotFoundError("Certificado do broker não encontrado.") 