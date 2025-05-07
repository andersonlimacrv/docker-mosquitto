import subprocess
import os
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(description="Gerar certificado de Autoridade Certificadora (CA).")
    parser.add_argument("--cn", type=str, default="CA_BROKER", help="Common Name (CN) do certificado da CA (padrão: CA_BROKER)")
    parser.add_argument("--days", type=int, default=3650, help="Validade do certificado em dias (padrão: 3650)")
    args = parser.parse_args()

    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)

    ca_key = certs_dir / "ca.key"
    ca_crt = certs_dir / "ca.crt"
    ca_srl = certs_dir / "ca.srl"

    print("🔐 Gerando chave privada da CA...")
    subprocess.run([
        "openssl", "genrsa", "-out", str(ca_key), "4096"
    ], check=True)

    print(f"📜 Gerando certificado da CA (autoassinado) com CN={args.cn} e validade de {args.days} dias...")
    subprocess.run([
        "openssl", "req", "-x509", "-new", "-nodes", "-key", str(ca_key),
        "-sha256", "-days", str(args.days), "-out", str(ca_crt),
        "-subj", f"/CN={args.cn}"
    ], check=True)

    print("✅ CA gerada com sucesso em:")
    print(f"  - {ca_key}")
    print(f"  - {ca_crt}")
    print(f"  - {ca_srl} (será criado ao assinar certificados)")

if __name__ == "__main__":
    main()
