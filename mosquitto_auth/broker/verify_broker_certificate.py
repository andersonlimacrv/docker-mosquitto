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
        return f"❌ Error executing: {' '.join(cmd)}\n{e.output or str(e)}"


def verify_broker_certificate(cert_path: Path = None, ca_cert_path: Path = None) -> dict:
    """Executa verificações completas no certificado e retorna um dicionário com os resultados"""
    
    if not cert_path:
        cert_path = settings.broker_cert_path
    if not ca_cert_path:
        ca_cert_path = settings.ca_cert_path

    if not cert_path.exists():
        return {"status": "ERROR", "message": f"❌ Certificado não encontrado: {cert_path}"}

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
        result_data["messages"].append(f"📅 Validade do certificado: {end_date_str}")

    result = run_cmd_capture(["openssl", "verify", "-CAfile", str(ca_cert_path), str(cert_path)])
    if "OK" in result:
        result_data["ca_verified"] = True
        result_data["messages"].append("✅ Certificado assinado pela CA confirmado")
    else:
        result_data["messages"].append(f"❌ Falha na verificação da CA:\n{result}")

    result = run_cmd_capture(["openssl", "x509", "-in", str(cert_path), "-text", "-noout"])

    if "Subject Alternative Name" in result:
        san_section = result.split("Subject Alternative Name:")[1].split("X509v3")[0]
        san_lines = [line.strip() for line in san_section.splitlines() if line.strip()]
        result_data["san_list"] = san_lines
        result_data["messages"].append("✅ Subject Alternative Names (SANs) presentes")
    else:
        result_data["messages"].append("❌ SANs não encontrados")

    if "Digital Signature" in result and "Key Encipherment" in result:
        result_data["key_usage_valid"] = True
        result_data["messages"].append("✅ Key Usage correto (digitalSignature, keyEncipherment)")
    else:
        result_data["messages"].append("❌ Key Usage incorreto")

    if "TLS Web Server Authentication" in result:
        result_data["extended_key_usage_valid"] = True
        result_data["messages"].append("✅ Extended Key Usage correto (serverAuth)")
    else:
        result_data["messages"].append("❌ Extended Key Usage incorreto")

    if (
        result_data["valid_until"]
        and result_data["ca_verified"]
        and result_data["key_usage_valid"]
        and result_data["extended_key_usage_valid"]
        and result_data["san_list"]
    ):
        result_data["status"] = "OK"
        result_data["messages"].append("✅ Todas as verificações passaram com sucesso!")

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
        print(f"❌ Erro na verificação: {str(e)}")


if __name__ == "__main__":
    main()
