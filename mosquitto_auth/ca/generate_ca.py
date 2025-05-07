import subprocess
import os
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate Certificate Authority (CA) certificate.")
    parser.add_argument("--cn", type=str, default="CA_BROKER", help="Common Name (CN) for the CA certificate (default: CA_BROKER)")
    parser.add_argument("--days", type=int, default=3650, help="Certificate validity in days (default: 3650)")
    args = parser.parse_args()

    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)

    ca_key = certs_dir / "ca.key"
    ca_crt = certs_dir / "ca.crt"
    ca_srl = certs_dir / "ca.srl"

    print("🔐 Generating CA private key...")
    subprocess.run([
        "openssl", "genrsa", "-out", str(ca_key), "4096"
    ], check=True)

    print(f"📜 Generating self-signed CA certificate with CN={args.cn} and validity of {args.days} days...")
    subprocess.run([
        "openssl", "req", "-x509", "-new", "-nodes", "-key", str(ca_key),
        "-sha256", "-days", str(args.days), "-out", str(ca_crt),
        "-subj", f"/CN={args.cn}"
    ], check=True)

    print("✅ CA successfully generated at:")
    print(f"  - {ca_key}")
    print(f"  - {ca_crt}")
    print(f"  - {ca_srl} (will be created when signing certificates)")

if __name__ == "__main__":
    main()