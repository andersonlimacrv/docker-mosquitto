import subprocess
from pathlib import Path
import argparse
from datetime import datetime
from mosquitto_auth.api.core.config import settings


def run_cmd_capture(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"[ERROR]: {' '.join(cmd)}\n{e.output or str(e)}"


def verify_broker_certificate(cert_path: Path = None, ca_cert_path: Path = None) -> dict:
    """Run full certificate verification and return a dictionary with the results"""
    
    if not cert_path:
        cert_path = settings.broker_cert_path
    if not ca_cert_path:
        ca_cert_path = settings.ca_cert_path

    if not cert_path.exists():
        return {"status": "ERROR", "message": f"❌ Certificate not found: {cert_path}"}

    result_data = {
        "cert_path": str(cert_path),
        "ca_cert_path": str(ca_cert_path),
        "valid_until": None,
        "ca_verified": False,
        "san_list": [],
        "key_usage_valid": False,
        "extended_key_usage_valid": False,
        "status": "FAIL",
        "messages": []
    }

    result = run_cmd_capture(["openssl", "x509", "-enddate", "-noout", "-in", str(cert_path)])
    if "notAfter=" in result:
        end_date_str = result.strip().split("=")[1]
        result_data["valid_until"] = end_date_str
        result_data["messages"].append(f"📅 Certificate validity: {end_date_str}")

    result = run_cmd_capture(["openssl", "verify", "-CAfile", str(ca_cert_path), str(cert_path)])
    if "OK" in result:
        result_data["ca_verified"] = True
        result_data["messages"].append("✅ Certificate signed by CA confirmed")
    else:
        result_data["messages"].append(f"❌ CA verification failed:\n{result}")

    result = run_cmd_capture(["openssl", "x509", "-in", str(cert_path), "-text", "-noout"])

    if "Subject Alternative Name" in result:
        san_section = result.split("Subject Alternative Name:")[1].split("X509v3")[0]
        san_lines = [line.strip() for line in san_section.splitlines() if line.strip()]
        result_data["san_list"] = san_lines
        result_data["messages"].append("✅ Subject Alternative Names (SANs) present")
    else:
        result_data["messages"].append("❌ SANs not found")

    if "Digital Signature" in result and "Key Encipherment" in result:
        result_data["key_usage_valid"] = True
        result_data["messages"].append("✅ Correct Key Usage (digitalSignature, keyEncipherment)")
    else:
        result_data["messages"].append("❌ Incorrect Key Usage")

    if "TLS Web Server Authentication" in result:
        result_data["extended_key_usage_valid"] = True
        result_data["messages"].append("✅ Correct Extended Key Usage (serverAuth)")
    else:
        result_data["messages"].append("❌ Incorrect Extended Key Usage")

    if (
        result_data["valid_until"]
        and result_data["ca_verified"]
        and result_data["key_usage_valid"]
        and result_data["extended_key_usage_valid"]
        and result_data["san_list"]
    ):
        result_data["status"] = "OK"
        result_data["messages"].append("✅ All verifications passed successfully!")

    return result_data


def main():
    parser = argparse.ArgumentParser(description="Verify MQTT broker certificate")
    parser.add_argument("--cert", type=Path, help="Path to broker certificate", default=None)
    parser.add_argument("--ca", type=Path, help="Path to CA certificate", default=None)
    args = parser.parse_args()

    try:
        result = verify_broker_certificate(args.cert, args.ca)
        from pprint import pprint
        pprint(result)
    except Exception as e:
        print(f"❌ Verification error: {str(e)}")


if __name__ == "__main__":
    main()
    