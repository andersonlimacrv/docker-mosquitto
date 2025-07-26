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
  summary="Gerar certificado da Autoridade Certificadora (CA)"
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
      detail=f"Erro ao gerar certificado da CA: {e}"
    )
  
@router.get(
  "/verify",
  status_code=status.HTTP_200_OK,
  summary="Verificar certificado da Autoridade Certificadora (CA)"
)
async def verify_ca():
  try:
    result = await asyncio.to_thread(verify_certificate)
    return result
  except FileNotFoundError:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Certificado da CA nao encontrado."
    )
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Erro ao verificar certificado da CA: {e}"
    )
  

@router.delete(
  "",
  status_code=status.HTTP_200_OK,
  summary="Remover certificado da Autoridade Certificadora (CA)"
)
async def delete_ca():
  try:
    await asyncio.to_thread(delete_ca_files)
    return {"message": "Certificado da CA removido com sucesso."}
  except FileNotFoundError:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Certificado da CA nao encontrado."
    )
  except Exception as e:
    raise HTTPException(
      status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
      detail=f"Erro ao remover certificado da CA: {e}"
)

  

