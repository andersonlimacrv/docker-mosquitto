import os
import subprocess
import sys
from pathlib import Path

DEFAULT_DAYS = 365
CERTS_BASE_DIR = Path("certs/client")
CA_CERT = Path("certs/ca.crt")
CA_KEY = Path("certs/ca.key")
CA_SERIAL = Path("certs/ca.srl")


def run_cmd(command: list[str]):
    """Executa um comando do sistema e exibe erro, se ocorrer."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {' '.join(command)}\n{e}")
        sys.exit(1)


def generate_client_certificate(cn: str, days: int):
    client_dir = CERTS_BASE_DIR / cn
    client_dir.mkdir(parents=True, exist_ok=True)

    key_path = client_dir / f"{cn}.key"
    csr_path = client_dir / f"{cn}.csr"
    crt_path = client_dir / f"{cn}.crt"

    # 1. Gera chave privada
    run_cmd(["openssl", "genrsa", "-out", str(key_path), "2048"])

    # 2. Gera CSR com CN (Common Name)
    run_cmd([
        "openssl", "req", "-new",
        "-key", str(key_path),
        "-out", str(csr_path),
        "-subj", f"/CN={cn}"
    ])

    # 3. Gera certificado assinado pela CA
    run_cmd([
        "openssl", "x509", "-req",
        "-in", str(csr_path),
        "-CA", str(CA_CERT),
        "-CAkey", str(CA_KEY),
        "-CAcreateserial",
        "-out", str(crt_path),
        "-days", str(days),
        "-sha256"
    ])

    print(f"✓ Certificado gerado com sucesso em: {client_dir}")


def main():
    if len(sys.argv) < 2:
        print("Uso: poetry run generate-cert <NOME_CLIENTE> [DIAS_VALIDADE]")
        sys.exit(1)

    cn = sys.argv[1]
    days = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_DAYS

    if not CA_CERT.exists() or not CA_KEY.exists():
        print("❌ Certificado ou chave da CA não encontrados em certs/ca.crt ou certs/ca.key")
        sys.exit(1)

    generate_client_certificate(cn, days)


if __name__ == "__main__":
    main()
