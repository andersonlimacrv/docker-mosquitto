import subprocess
import os
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(description="Gerar certificado do broker MQTT.")
    parser.add_argument("cn", type=str, help="Common Name (CN) obrigatório — IP ou domínio do broker.")
    parser.add_argument("--days", type=int, default=365, help="Validade do certificado em dias (padrão: 365)")
    args = parser.parse_args()

    broker_dir = Path("certs/broker")
    broker_dir.mkdir(parents=True, exist_ok=True)

    ca_key = Path("certs/ca.key")
    ca_crt = Path("certs/ca.crt")

    broker_key = broker_dir / "broker.key"
    broker_csr = broker_dir / "broker.csr"
    broker_crt = broker_dir / "broker.crt"

    print("🔐 Gerando chave privada do broker...")
    subprocess.run([
        "openssl", "genrsa", "-out", str(broker_key), "2048"
    ], check=True)

    print(f"📄 Gerando CSR para o broker com CN={args.cn}...")
    subprocess.run([
        "openssl", "req", "-new", "-key", str(broker_key),
        "-out", str(broker_csr),
        "-subj", f"/CN={args.cn}"
    ], check=True)

    print("✅ Assinando certificado com a CA...")
    subprocess.run([
        "openssl", "x509", "-req", "-in", str(broker_csr),
        "-CA", str(ca_crt), "-CAkey", str(ca_key),
        "-CAcreateserial", "-out", str(broker_crt),
        "-days", str(args.days), "-sha256"
    ], check=True)

    print("🏁 Certificado do broker gerado com sucesso em:")
    print(f"  - {broker_key}")
    print(f"  - {broker_csr}")
    print(f"  - {broker_crt}")

if __name__ == "__main__":
    main()
