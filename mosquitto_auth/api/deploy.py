from fastapi import APIRouter, Header, HTTPException
from mosquitto_auth.api.config import API_KEY, PROJECT_ROOT
import subprocess
import os

router = APIRouter()

@router.post("/deploy")
def webhook_deploy(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        result = subprocess.run(["git", "pull"], cwd=PROJECT_ROOT, capture_output=True, text=True, check=True)
        return {
            "message": "Repository updated successfully.",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail={
            "error": "Failed to pull repository.",
            "stdout": e.stdout,
            "stderr": e.stderr
        })
