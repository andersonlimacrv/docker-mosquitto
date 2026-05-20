from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager
from mosquitto_auth.client.certificate.generate_users_certificate import generate_client_certificate

router = APIRouter()

class ProvisionResponse(BaseModel):
    message: str
    user: str
    certificate_created: bool
    user_created: bool

@router.post("", response_model=ProvisionResponse, status_code=status.HTTP_200_OK)
def provision_monitor_user():
    """
    Gera o usuário reservado (sys_monitor) e o certificado TLS para que a API 
    consiga se conectar internamente e fazer as inscrições de métricas.
    """
    user = settings.USER_MQTT_MONITOR
    passwd = settings.PASSWD_MQTT_MONITOR
    
    user_created = False
    certificate_created = False
    messages = []
    
    # 1. Provisiona usuário
    try:
        manager = MosquittoUserManager(passwd_file=settings.PASSWD_FILE_PATH)
        users = manager.list_users()
        if user not in users:
            manager.add_user(user, passwd)
            user_created = True
            messages.append("Usuário criado no mosquitto.passwd.")
        else:
            messages.append("Usuário já existia no mosquitto.passwd.")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao provisionar usuário de monitoramento: {e}"
        )

    # 2. Provisiona certificado
    cert_dir = settings.certs_dir / "client" / user
    cert_path = cert_dir / f"{user}.crt"
    
    if not cert_path.exists():
        try:
            # Requisita que o CN seja igual ao username 
            generate_client_certificate(cn=user, days=3650)
            certificate_created = True
            messages.append("Certificado criado com sucesso.")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao provisionar certificado TLS: {e}"
            )
    else:
        messages.append("Certificado já existia.")

    return ProvisionResponse(
        message=" | ".join(messages),
        user=user,
        user_created=user_created,
        certificate_created=certificate_created
    )
