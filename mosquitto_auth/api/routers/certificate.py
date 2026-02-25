import asyncio
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, Response
import zipfile
import io
import shutil
import re
from mosquitto_auth.api.models.certificate import (
    CertificateCreate, CertificateResponse, CertificateVerificationResponse,
    BrokerCertificateResponse, BrokerCertificateVerificationResponse, BrokerCertificateDeleteResponse, BrokerCertificateRequest
)
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.api.models.status import CertificateStatus
from mosquitto_auth.api.models.responses import CertificateMessages
from mosquitto_auth.client.certificate.generate_users_certificate import generate_client_certificate, CA_CERT, CA_KEY, CERTS_BASE_DIR
from mosquitto_auth.client.certificate.delete_user_certificate import delete_user_certificate
from mosquitto_auth.client.certificate.verify_client_certificate import verify_certificate_client
from mosquitto_auth.broker.generate_broker_certificate import generate_broker_certificate
from mosquitto_auth.broker.delete_broker_certificate import delete_broker_certificate as delete_broker_cert_func
from mosquitto_auth.broker.verify_broker_certificate import verify_broker_certificate 
from mosquitto_auth.lib.utils import interpret_openssl_error, error_openssl_map
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
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A certificate or key not found."
            )
        await asyncio.to_thread(
            generate_client_certificate, data.username, data.days if data.days is not None else 365, False
        )
        cert_dir = CERTS_BASE_DIR / data.username
        crt_path = cert_dir / f"{data.username}.crt"
        key_path = cert_dir / f"{data.username}.key"
        if not crt_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User '{data.username}' not found."
            )
        message = CertificateMessages.CERTIFICATE_CREATED.format(username=data.username)
        return CertificateResponse(
            username=data.username,
            status=CertificateStatus.CREATED,
            message=message
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
    summary="List all user certificates"
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
    summary="Download certificate and key of user (.zip)"
)
async def get_client_certificate_bundle(username: str):
    cert_dir = CERTS_BASE_DIR / username
    cert_path = cert_dir / f"{username}.crt"
    key_path = cert_dir / f"{username}.key"
    if not cert_path.exists() or not key_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate or key for user '{username}' not found."
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
    summary="Verify certificate information for a user",
    response_model=CertificateVerificationResponse
)
async def get_client_certificate_verification(username: str):
    result = await asyncio.to_thread(verify_certificate_client, username)

    validity = None
    expiration = None
    signature_status = "[NOT AVAILABLE]"
    error_description = None

    for line in result.splitlines():
        line = line.strip()

        if line.startswith("notBefore="):
            validity = line.replace("notBefore=", "")
        elif line.startswith("notAfter="):
            expiration = line.replace("notAfter=", "")
        elif ": OK" in line:
            signature_status = "OK"
        else:
            interpreted = interpret_openssl_error(line)
            if interpreted:
                tag, description = interpreted
                signature_status = tag
                error_description = description 

    return CertificateVerificationResponse(
        valid_from=validity,
        valid_until=expiration,
        signature_status=signature_status, 
        error_description=error_description 
    )


@router.delete(
    "/client/{username}",
    status_code=status.HTTP_200_OK,
    summary="Remove certificate and key of user"
)
async def delete_client_certificate(username: str):
    try:
        delete_user_certificate(username)
        return {"message": f"Certificate and key for user '{username}' removed successfully."}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Certificate directory for user '{username}' not found."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing certificate: {e}"
        )


@router.post(
    "/broker",
    response_model=BrokerCertificateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate broker certificate"
)
async def create_broker_certificate(data: BrokerCertificateRequest):
    try:
        await asyncio.to_thread(generate_broker_certificate, settings.BROKER_CN, data.days, False)
        return BrokerCertificateResponse(
            username="broker",
            status=CertificateStatus.CREATED,
            message="Broker certificate generated successfully."
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error generating broker certificate: {e}")

@router.get(
    "/broker/verify",
    response_model=BrokerCertificateVerificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify broker certificate information"
)
async def get_verify_broker_certificate():
    try:
        result = await asyncio.to_thread(verify_broker_certificate)

        if result.get("status") == "ERROR":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("message", "Certificate not found.")
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
            detail=f"Error verifying broker certificate: {e}"
        )

@router.delete(
    "/broker",
    response_model=BrokerCertificateDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Remove broker certificate"
)
async def delete_broker_certificate():
    try:
        await asyncio.to_thread(delete_broker_cert_func)
        return BrokerCertificateDeleteResponse(message="Broker certificate and key removed successfully.")
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Broker certificate not found.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error removing broker certificate: {e}")

