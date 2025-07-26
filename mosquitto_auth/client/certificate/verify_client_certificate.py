import sys
from pathlib import Path
import subprocess
from mosquitto_auth.api.core.config import settings

CA_CERT = settings.ca_cert_path
CLIENT_BASE = settings.client_certs_dir

def run_cmd(cmd: list[str]):
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing: {' '.join(cmd)}\n{e}")
        sys.exit(1)

def run_cmd_capture(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"❌ Error executing: {' '.join(cmd)}\n{e.output or e}"
    

def verify_certificate_client(cn: str) -> str:
    client_dir = CLIENT_BASE / cn
    crt_path = client_dir / f"{cn}.crt"

    if not crt_path.exists():
        return f"❌ Certificate not found: {crt_path}"

    if not CA_CERT.exists():
        return f"❌ CA certificate not found: {CA_CERT}"

    output = []
    output.append("🔍 Checking certificate validity:")
    output.append(run_cmd_capture(["openssl", "x509", "-in", str(crt_path), "-noout", "-dates"]))

    output.append("\n🔒 Verifying CA signature:")
    output.append(run_cmd_capture(["openssl", "verify", "-CAfile", str(CA_CERT), str(crt_path)]))

    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: poetry run verify-cert <CN>")
        sys.exit(1)

    cn = sys.argv[1]
    print(verify_certificate_client(cn))


if __name__ == "__main__":
    main()