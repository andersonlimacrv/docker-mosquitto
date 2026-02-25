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

    print("🔐 Generating CA private key...")
    subprocess.run([
        "openssl", "genrsa", "-out", str(ca_key), "4096"
    ], check=True)

    print(f"📜 Generating self-signed CA certificate with CN={cn} and validity of {days} days...")
    subprocess.run([
        "openssl", "req", "-x509", "-new", "-nodes", "-key", str(ca_key),
        "-sha256", "-days", str(days), "-out", str(ca_crt),
        "-subj", f"/CN={cn}"
    ], check=True)

    print("✅ CA successfully generated at:")
    print(f"  - {ca_key}")
    print(f"  - {ca_crt}")
    print(f"  - {ca_srl} (will be created when signing certificates)")

    return {
        "ca_key": str(ca_key),
        "ca_crt": str(ca_crt),
        "ca_srl": str(ca_srl),
        "common_name": cn,
        "valid_days": days
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Certificate Authority (CA) certificate.")
    parser.add_argument("--cn", type=str, default="ROOT_BROKER_CA", help="Common Name (CN) for the CA certificate (default: ROOT_BROKER_CA)")
    parser.add_argument("--days", type=int, default=3650, help="Certificate validity in days (default: 3650)")
    args = parser.parse_args()

    generate_ca(args.cn, args.days)

if __name__ == "__main__":
    main()
