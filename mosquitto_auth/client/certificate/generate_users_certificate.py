import os
import subprocess
import sys
from pathlib import Path
import argparse
from mosquitto_auth.api.core.config import settings

DEFAULT_DAYS = 365
CERTS_BASE_DIR = settings.client_certs_dir
CA_CERT = settings.ca_cert_path 
CA_KEY = settings.ca_key_path

def run_cmd(command: list[str]):
    """
    Execute a command on the system and display error if it occurs.
    """
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {' '.join(command)}\n{e}")
        sys.exit(1)

def generate_openssl_config(cn: str, config_path: Path):
    """Generate  config temp file for the Openssl."""
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

    generate_openssl_config(cn, config_path)

    run_cmd(["openssl", "genrsa", "-out", str(key_path), "2048"])

    run_cmd([
        "openssl", "req", "-new",
        "-key", str(key_path),
        "-out", str(csr_path),
        "-config", str(config_path)
    ])

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

    if not keep_temp:
        temp_files = [csr_path, config_path]
        for file in temp_files:
            try:
                file.unlink()
            except Exception as e:
                print(f"⚠️ Warning: Could not remove temporary file {file}: {e}")

    print(f"""
✅ Client certificate generated successfully!
Files in: {client_dir}
- Private key: {key_path}
- Certificate: {crt_path}
""")

def main():
    parser = argparse.ArgumentParser(description="Generator of MQTT client certificates.")
    parser.add_argument("cn", help="Common Name (Identifier of the client, e.g., username)")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Validity in days")
    parser.add_argument("--keep-temp", action="store_true", help="If set, temporary files (CSR and config) will not be deleted after generation")
    args = parser.parse_args()

    if not CA_CERT.exists() or not CA_KEY.exists():
        print("❌ Certificate or CA key not found in '{CA_CERT}' or '{CA_KEY}'. Please generate the CA certificate first.")
        sys.exit(1)

    generate_client_certificate(args.cn, args.days, args.keep_temp)

if __name__ == "__main__":
    main()