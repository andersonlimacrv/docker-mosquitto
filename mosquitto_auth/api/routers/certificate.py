import asyncio
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, Response
import zipfile
import io
import shutil
import re
from mosquitto_auth.api.models.certificate import (
    CertificateCreate, CertificateResponse, CertificateVerificationResponse,
    BrokerCertificateResponse, BrokerCertificateVerificationResponse, BrokerCertificateDeleteResponse
)
from mosquitto_auth.api.models.status import CertificateStatus
from mosquitto_auth.api.models.responses import CertificateMessages
from mosquitto_auth.client.certificate.generate_users_certificate import generate_client_certificate, CA_CERT, CA_KEY, CERTS_BASE_DIR
from mosquitto_auth.client.certificate.delete_user_certificate import delete_user_certificate
from mosquitto_auth.client.certificate.verify_client_certificate import verify_certificate_client
from mosquitto_auth.broker.generate_broker_certificate import generate_broker_certificate
from mosquitto_auth.broker.delete_broker_certificate import delete_broker_certificate as delete_broker_cert_func
from mosquitto_auth.broker.verify_broker_certificate import verify_broker_certificate 

router = APIRouter()

@router.post(
    "/client",
    response_model=CertificateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_certificate(data: CertificateCreate) -> CertificateResponse:
    try:
        if not CA_CERT.exists() or not CA_KEY.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Certificado ou chave da CA não encontrados."
            )
        await asyncio.to_thread(
            generate_client_certificate, data.username, data.days if data.days is not None else 365, False
        )
        cert_dir = CERTS_BASE_DIR / data.username
        crt_path = cert_dir / f"{data.username}.crt"
        key_path = cert_dir / f"{data.username}.key"
        if not crt_path.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Certificado não foi gerado para '{data.username}'."
            )
        message = CertificateMessages.CERTIFICATE_CREATED.format(username=data.username)
        return CertificateResponse(
            username=data.username,
            status=CertificateStatus.CREATED,
            message=message,
            cert_path=str(crt_path),
            key_path=str(key_path)
        )
    except Exception as e:
        message = CertificateMessages.CERTIFICATE_ERROR.format(username=data.username)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{message}: {e}"
        )


@router.get(
    "/client",
    status_code=status.HTTP_200_OK,
    summary="Listar todos os certificados de usuário"
)
async def list_client_certificates():
    if not CERTS_BASE_DIR.exists() or not CERTS_BASE_DIR.is_dir():
        return {"certificates": []}
    users = [p.name for p in CERTS_BASE_DIR.iterdir() if p.is_dir()]
    return {"certificates": users}


@router.get(
    "/client/{username}",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
    summary="Baixar certificado e chave do usuário (.zip)"
)
async def get_client_certificate_bundle(username: str):
    cert_dir = CERTS_BASE_DIR / username
    cert_path = cert_dir / f"{username}.crt"
    key_path = cert_dir / f"{username}.key"
    if not cert_path.exists() or not key_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificado ou chave para '{username}' não encontrado(s)."
        )
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        zipf.write(cert_path, arcname=f"{username}.crt")
        zipf.write(key_path, arcname=f"{username}.key")
    zip_buffer.seek(0)
    return Response(
        content=zip_buffer.read(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename={username}_cert_bundle.zip"
        }
    )


@router.get(
    "/client/{username}/verify",
    status_code=status.HTTP_200_OK,
    summary="Verificar informações do certificado do usuário",
    response_model=CertificateVerificationResponse
)
async def get_client_certificate_verification(username: str):
    result = await asyncio.to_thread(verify_certificate_client, username)
    if result.startswith("❌"):
        raise HTTPException(status_code=404, detail=result)

    validity = None
    expiration = None
    signature_status = None
    for line in result.splitlines():
        if line.strip().startswith("notBefore="):
            validity = line.strip().replace("notBefore=", "")
        elif line.strip().startswith("notAfter="):
            expiration = line.strip().replace("notAfter=", "")
        elif ": OK" in line:
            signature_status = "OK"
        elif ": " in line and not signature_status:
            signature_status = line.split(":", 1)[-1].strip()

    return CertificateVerificationResponse(
        valid_from=validity,
        valid_until=expiration,
        signature_status=signature_status
    )


@router.delete(
    "/client/{username}",
    status_code=status.HTTP_200_OK,
    summary="Remover certificado e chave do usuário"
)
async def delete_client_certificate(username: str):
    try:
        delete_user_certificate(username)
        return {"message": f"Certificado e chave de '{username}' removidos com sucesso."}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Diretório de certificado para '{username}' não encontrado."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao remover certificado: {e}"
        )


@router.post(
    "/broker",
    response_model=BrokerCertificateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Gerar certificado do broker"
)
async def create_broker_certificate(cn: str = None, days: int = 365):
    try:
        await asyncio.to_thread(generate_broker_certificate, cn, days, False)
        return BrokerCertificateResponse(
            username="broker",
            status=CertificateStatus.CREATED,
            message="Certificado do broker gerado com sucesso."
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao gerar certificado do broker: {e}")

@router.get(
    "/broker/verify",
    response_model=BrokerCertificateVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar certificado do broker"
)
async def get_verify_broker_certificate():
    try:
        result = await asyncio.to_thread(verify_broker_certificate)

        if result.get("status") == "ERROR":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("message", "Certificado não encontrado.")
            )

        valid_until = result.get("valid_until")
        ca_signature = "OK" if result.get("ca_verified") else None
        san_raw = result.get("san_list", [])
        san = []

        for entry in san_raw:
            if "IP Address:" in entry:
                ip_parts = entry.replace("IP Address:", "").split(",")
                san.extend([f"IP: {ip.strip()}" for ip in ip_parts if ip.strip()])
            elif "DNS:" in entry:
                dns_parts = entry.replace("DNS:", "").split(",")
                san.extend([f"DNS: {dns.strip()}" for dns in dns_parts if dns.strip()])

        key_usage = "OK" if result.get("key_usage_valid") else None
        extended_key_usage = "OK" if result.get("extended_key_usage_valid") else None
        status_value = result.get("status")

        return BrokerCertificateVerificationResponse(
            valid_until=valid_until,
            ca_signature=ca_signature,
            san=san or None,
            key_usage=key_usage,
            extended_key_usage=extended_key_usage,
            status=status_value
        )

    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao verificar certificado do broker: {e}"
        )

@router.delete(
    "/broker",
    response_model=BrokerCertificateDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Remover certificado do broker"
)
async def delete_broker_certificate():
    try:
        await asyncio.to_thread(delete_broker_cert_func)
        return BrokerCertificateDeleteResponse(message="Certificado e chave do broker removidos com sucesso.")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Certificado do broker não encontrado.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao remover certificado do broker: {e}")

