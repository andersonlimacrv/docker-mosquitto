import asyncio
from fastapi import APIRouter, HTTPException, status
from mosquitto_auth.ca.generate_ca import generate_ca
from mosquitto_auth.ca.verify_ca import verify_certificate
from mosquitto_auth.ca.delete_ca import delete_ca_files
from mosquitto_auth.api.models.ca import CreateCA, CACreateResponse

router = APIRouter()

@router.post(
  "",
  response_model=CACreateResponse,
  status_code=status.HTTP_201_CREATED,
  summary="Generate Certificate Authority (CA) certificate"
)
async def create_ca(data: CreateCA):
  try:
    result = await asyncio.to_thread(generate_ca, data.common_name, data.days)
    if result .get("status") == "ERROR":
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=result.get("message")
      )
    return result
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Error generating CA certificate: {e}"
    )
  
@router.get(
  "/verify",
  status_code=status.HTTP_200_OK,
  summary="Verify Certificate Authority (CA) certificate"
)
async def verify_ca():
  try:
    result = await asyncio.to_thread(verify_certificate)
    return result
  except FileNotFoundError:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="A certificate not found."
    )
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Error verifying CA certificate: {e}"
    )
  

@router.delete(
  "",
  status_code=status.HTTP_200_OK,
  summary="Remove Certificate Authority (CA) certificate"
)
async def delete_ca():
  try:
    await asyncio.to_thread(delete_ca_files)
    return {"message": "Certificate Authority (CA) certificate removed successfully."}
  except FileNotFoundError:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Certificate Authority (CA) certificate not found."
    )
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Error removing CA certificate: {e}"
)

  

