import argparse
import subprocess
import re
from pathlib import Path
from mosquitto_auth.api.core.config import settings


def extract_match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else None

def verify_certificate(cert_path: Path = settings.ca_cert_path) -> dict:
    if not cert_path.exists():
        return {"status": "ERROR", "message": f"❌ Certificado nao encontrado: {cert_path}"}
    try:
        cmd = subprocess.run(
            ["openssl", "x509", "-in", str(cert_path), "-noout", "-text"],
            capture_output=True,
            text=True,
            check=True
        )

        output = cmd.stdout
        issuer = extract_match(r"Issuer: (.+)", output)
        subject = extract_match(r"Subject: (.+)", output)
        not_before = extract_match(r"Not Before:\s+(.+)", output)
        not_after = extract_match(r"Not After\s*:\s+(.+)", output)

        print("✅ Certificado verificado com sucesso!")
        print(f"  - Issuer: {issuer if issuer else 'N/A'}")
        print(f"  - Subject: {subject if subject else 'N/A'}")
        print(f"  - Valid Before: {not_before if not_before else 'N/A'}")
        print(f"  - Valid until: {not_after if not_after else 'N/A'}")

        return {
            "issuer": issuer,
            "subject": subject,
            "valid_not_before": not_before,
            "valid_not_after": not_after,
            "status": "OK"
        }

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Erro ao verificar o certificado: {e.stderr}")


def main():
    parser = argparse.ArgumentParser(description="Verifica o certificado da Autoridade Certificadora (CA).")
    parser.add_argument("--cert", type=Path, help="Caminho para o certificado da CA", default=settings.ca_cert_path)
    args = parser.parse_args()

    verify_certificate(args.cert)


if __name__ == "__main__":
    main()
