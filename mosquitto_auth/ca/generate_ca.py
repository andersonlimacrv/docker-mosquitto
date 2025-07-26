import argparse
import subprocess
from mosquitto_auth.api.core.config import settings

def create_initial_cert_paths() -> bool:
  certs_dir = settings.certs_dir
  certs_dir.mkdir(exist_ok=True)
  if not certs_dir.exists():
    return False
  return True
  

def generate_ca(cn: str = "ROOT_BROKER_CA", days: int = 3650) -> dict:
    certs_dir = settings.certs_dir
    certs_dir.mkdir(exist_ok=True)

    ca_key = certs_dir / "ca.key"
    ca_crt = certs_dir / "ca.crt"
    ca_srl = certs_dir / "ca.srl"

    print("🔐 Gerando chave privada da CA...")
    subprocess.run([
        "openssl", "genrsa", "-out", str(ca_key), "4096"
    ], check=True)

    print(f"📜 Gerando certificado autoassinado da CA com CN={cn} e validade de {days} dias...")
    subprocess.run([
        "openssl", "req", "-x509", "-new", "-nodes", "-key", str(ca_key),
        "-sha256", "-days", str(days), "-out", str(ca_crt),
        "-subj", f"/CN={cn}"
    ], check=True)

    print("✅ CA gerada com sucesso em:")
    print(f"  - {ca_key}")
    print(f"  - {ca_crt}")
    print(f"  - {ca_srl} (será criado ao assinar certificados)")

    return {
        "ca_key": str(ca_key),
        "ca_crt": str(ca_crt),
        "ca_srl": str(ca_srl),
        "common_name": cn,
        "valid_days": days
    }


def main():
    parser = argparse.ArgumentParser(description="Gera certificado da Autoridade Certificadora (CA).")
    parser.add_argument("--cn", type=str, default="ROOT_BROKER_CA", help="Common Name (CN) para o certificado da CA (padrão: CN_BROKER)")
    parser.add_argument("--days", type=int, default=3650, help="Validade do certificado em dias (padrão: 3650)")
    args = parser.parse_args()

    generate_ca(args.cn, args.days)

if __name__ == "__main__":
    main()
