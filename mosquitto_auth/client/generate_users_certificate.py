import os
import subprocess
import sys
from pathlib import Path
import argparse

DEFAULT_DAYS = 365
CERTS_BASE_DIR = Path("certs/client")
CA_CERT = Path("certs/ca.crt")
CA_KEY = Path("certs/ca.key")

def run_cmd(command: list[str]):
    """Executa um comando do sistema e exibe erro, se ocorrer."""
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {' '.join(command)}\n{e}")
        sys.exit(1)

def generate_openssl_config(cn: str, config_path: Path):
    """Gera arquivo de configuração temporário para o openssl"""
    config_path.write_text(f"""
[ req ]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[ req_distinguished_name ]
CN = {cn}

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
""")

def generate_client_certificate(cn: str, days: int, keep_temp: bool = False):
    client_dir = CERTS_BASE_DIR / cn
    client_dir.mkdir(parents=True, exist_ok=True)

    key_path = client_dir / f"{cn}.key"
    csr_path = client_dir / f"{cn}.csr"
    crt_path = client_dir / f"{cn}.crt"
    config_path = client_dir / "openssl.cnf"

    # 1. Gera arquivo de configuração
    generate_openssl_config(cn, config_path)

    # 2. Gera chave privada
    run_cmd(["openssl", "genrsa", "-out", str(key_path), "2048"])

    # 3. Gera CSR
    run_cmd([
        "openssl", "req", "-new",
        "-key", str(key_path),
        "-out", str(csr_path),
        "-config", str(config_path)
    ])

    # 4. Assina o certificado
    run_cmd([
        "openssl", "x509", "-req",
        "-in", str(csr_path),
        "-CA", str(CA_CERT),
        "-CAkey", str(CA_KEY),
        "-CAcreateserial",
        "-out", str(crt_path),
        "-days", str(days),
        "-sha256",
        "-extfile", str(config_path),
        "-extensions", "v3_req"
    ])

    # 5. Limpeza
    if not keep_temp:
        temp_files = [csr_path, config_path]
        for file in temp_files:
            try:
                file.unlink()
            except Exception as e:
                print(f"⚠️ Não foi possível remover {file}: {e}")

    print(f"""
✅ Certificado de cliente gerado com sucesso!
Arquivos em: {client_dir}
- Chave privada: {key_path}
- Certificado: {crt_path}
""")

def main():
    parser = argparse.ArgumentParser(description="Gerador de certificados para clientes MQTT")
    parser.add_argument("cn", help="Common Name (identificação do cliente)")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Validade em dias")
    parser.add_argument("--keep-temp", action="store_true", help="Manter arquivos temporários")
    args = parser.parse_args()

    if not CA_CERT.exists() or not CA_KEY.exists():
        print("❌ Certificado ou chave da CA não encontrados em certs/")
        sys.exit(1)

    generate_client_certificate(args.cn, args.days, args.keep_temp)

if __name__ == "__main__":
    main()