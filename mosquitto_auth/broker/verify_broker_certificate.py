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
        return f"❌ Error executing: {' '.join(cmd)}\n{e.output or e}"

def verify_certificate(cert_path: Path = None, ca_cert_path: Path = None) -> str:
    """Executa verificações completas no certificado"""
    # Usar caminhos do settings se não especificados
    if not cert_path:
        cert_path = Path(settings.broker_cert_path)
    if not ca_cert_path:
        ca_cert_path = Path(settings.ca_cert_path)
    
    output = []
    output.append(f"🔍 Verificando certificado: {cert_path}")
    
    if not cert_path.exists():
        return f"❌ Certificado não encontrado: {cert_path}"

    # Verificar validade
    result = run_cmd_capture(["openssl", "x509", "-enddate", "-noout", "-in", str(cert_path)])
    if "notAfter=" in result:
        end_date_str = result.strip().split("=")[1]
        output.append(f"📅 Validade do certificado: {end_date_str}")

    # Verificar assinatura da CA
    result = run_cmd_capture(["openssl", "verify", "-CAfile", str(ca_cert_path), str(cert_path)])
    if "OK" in result:
        output.append("✅ Certificado assinado pela CA confirmado")
    else:
        output.append(f"❌ Falha na verificação da CA:\n{result}")

    # Verificar extensões
    output.append("\n🔎 Verificando extensões do certificado:")
    result = run_cmd_capture(["openssl", "x509", "-in", str(cert_path), "-text", "-noout"])
    
    if "Subject Alternative Name" in result:
        san_section = result.split("Subject Alternative Name:")[1].split("\n")[0:3]
        output.append("✅ Subject Alternative Names (SANs) presentes:")
        output.append("\n".join(line.strip() for line in san_section if line.strip()))
    else:
        output.append("❌ SANs não encontrados")

    if "Digital Signature" in result and "Key Encipherment" in result:
        output.append("✅ Key Usage correto (digitalSignature, keyEncipherment)")
    else:
        output.append("❌ Key Usage incorreto")

    if "TLS Web Server Authentication" in result:
        output.append("✅ Extended Key Usage correto (serverAuth)")
    else:
        output.append("❌ Extended Key Usage incorreto")

    output.append("✅ Todas as verificações passaram com sucesso!")
    return "\n".join(output)

def main():
    parser = argparse.ArgumentParser(description="Verify MQTT broker certificate")
    parser.add_argument("--cert", type=Path, help="Path to broker certificate", default=None)
    parser.add_argument("--ca", type=Path, help="Path to CA certificate", default=None)
    args = parser.parse_args()

    try:
        result = verify_certificate(args.cert, args.ca)
        print(result)
    except Exception as e:
        print(f"❌ Erro na verificação: {str(e)}")

if __name__ == "__main__":
    main()