import sys
from pathlib import Path
import subprocess
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.lib.utils import interpret_openssl_error

CA_CERT = settings.ca_cert_path
CLIENT_BASE = settings.client_certs_dir


def run_cmd_capture(cmd: list[str]) -> str:
    """Run a shell command and capture stdout + stderr."""
    try:
        result = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR]: {' '.join(cmd)}\n{e.output or str(e)}"


def verify_certificate_client(cn: str) -> str:
    """Check the validity and CA signature of a client certificate."""
    client_dir = CLIENT_BASE / cn
    crt_path = client_dir / f"{cn}.crt"

    if not crt_path.exists():
        return "[CLIENT NOT FOUND] Client certificate not found: {crt_path}"

    if not CA_CERT.exists():
        return "[CA NOT FOUND] CA certificate not found: {CA_CERT}"

    output = []
    output.append("🔍 Checking certificate validity:")
    output.append(
        run_cmd_capture([
            "openssl", "x509", "-in", str(crt_path), "-noout", "-dates"
        ])
    )

    output.append("\n🔒 Verifying CA signature:")
    verify_output = run_cmd_capture([
        "openssl", "verify", "-CAfile", str(CA_CERT), str(crt_path)
    ])
    output.append(verify_output)
    interpreted = interpret_openssl_error(verify_output)
    if interpreted:
        tag, description = interpreted
        output.append(f"\n💡 {tag} {description}")

    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("Usage: poetry run verify-client-cert <CN>")
        sys.exit(1)

    cn = sys.argv[1]
    print(verify_certificate_client(cn))


if __name__ == "__main__":
    main()
