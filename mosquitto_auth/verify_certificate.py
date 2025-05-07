import sys
from pathlib import Path
import subprocess

CA_CERT = Path("certs/ca.crt")
CLIENT_BASE = Path("certs/client")


def run_cmd(cmd: list[str]):
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error executing: {' '.join(cmd)}\n{e}")
        sys.exit(1)


def verify_certificate(cn: str):
    client_dir = CLIENT_BASE / cn
    crt_path = client_dir / f"{cn}.crt"

    if not crt_path.exists():
        print(f"❌ Certificate not found: {crt_path}")
        sys.exit(1)

    if not CA_CERT.exists():
        print(f"❌ CA certificate not found: {CA_CERT}")
        sys.exit(1)

    print("🔍 Checking certificate validity:")
    run_cmd(["openssl", "x509", "-in", str(crt_path), "-noout", "-dates"])

    print("\n🔒 Verifying CA signature:")
    run_cmd(["openssl", "verify", "-CAfile", str(CA_CERT), str(crt_path)])


def main():
    if len(sys.argv) < 2:
        print("Usage: poetry run verify-cert <CN>")
        sys.exit(1)

    cn = sys.argv[1]
    verify_certificate(cn)


if __name__ == "__main__":
    main()