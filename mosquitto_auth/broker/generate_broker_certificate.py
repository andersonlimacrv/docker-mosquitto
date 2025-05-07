import subprocess
import os
from pathlib import Path
import argparse

def main():
    parser = argparse.ArgumentParser(description="Generate MQTT broker certificate.")
    parser.add_argument("cn", type=str, help="Required Common Name (CN) — broker IP or domain.")
    parser.add_argument("--days", type=int, default=365, help="Certificate validity in days (default: 365)")
    args = parser.parse_args()

    broker_dir = Path("certs/broker")
    broker_dir.mkdir(parents=True, exist_ok=True)

    ca_key = Path("certs/ca.key")
    ca_crt = Path("certs/ca.crt")

    broker_key = broker_dir / "broker.key"
    broker_csr = broker_dir / "broker.csr"
    broker_crt = broker_dir / "broker.crt"

    print("🔐 Generating broker private key...")
    subprocess.run([
        "openssl", "genrsa", "-out", str(broker_key), "2048"
    ], check=True)

    print(f"📄 Generating CSR for broker with CN={args.cn}...")
    subprocess.run([
        "openssl", "req", "-new", "-key", str(broker_key),
        "-out", str(broker_csr),
        "-subj", f"/CN={args.cn}"
    ], check=True)

    print("✅ Signing certificate with CA...")
    subprocess.run([
        "openssl", "x509", "-req", "-in", str(broker_csr),
        "-CA", str(ca_crt), "-CAkey", str(ca_key),
        "-CAcreateserial", "-out", str(broker_crt),
        "-days", str(args.days), "-sha256"
    ], check=True)

    print("🏁 Broker certificate successfully generated at:")
    print(f"  - {broker_key}")
    print(f"  - {broker_csr}")
    print(f"  - {broker_crt}")

if __name__ == "__main__":
    main()