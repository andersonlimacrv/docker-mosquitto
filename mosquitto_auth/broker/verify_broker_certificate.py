import subprocess
from pathlib import Path
import argparse
from datetime import datetime

def verify_certificate(cert_path: Path, ca_cert_path: Path):
    """Executa verificações completas no certificado"""
    print(f"🔍 Verificando certificado: {cert_path}")
    
    if not cert_path.exists():
        raise FileNotFoundError(f"Certificado não encontrado: {cert_path}")

    check_certificate_expiry(cert_path)
    verify_ca_signature(cert_path, ca_cert_path)
    verify_certificate_extensions(cert_path)
    print("✅ Todas as verificações passaram com sucesso!")

def check_certificate_expiry(cert_path: Path):
    """Verifica a data de expiração do certificado"""
    result = subprocess.run(
        ["openssl", "x509", "-enddate", "-noout", "-in", str(cert_path)],
        capture_output=True,
        text=True,
        check=True
    )
    
    end_date_str = result.stdout.strip().split("=")[1]
    print(f"📅 Validade do certificado: {end_date_str}")

def verify_ca_signature(cert_path: Path, ca_cert_path: Path):
    """Verifica se o certificado foi assinado pela CA"""
    result = subprocess.run(
        ["openssl", "verify", "-CAfile", str(ca_cert_path), str(cert_path)],
        capture_output=True,
        text=True
    )
    
    if "OK" in result.stdout:
        print("✅ Certificado assinado pela CA confirmado")
    else:
        raise ValueError(f"❌ Falha na verificação da CA:\n{result.stderr}")

def verify_certificate_extensions(cert_path: Path):
    """Verifica extensões críticas do certificado"""
    print("\n🔎 Verificando extensões do certificado:")
    
    result = subprocess.run(
        ["openssl", "x509", "-in", str(cert_path), "-text", "-noout"],
        capture_output=True,
        text=True,
        check=True
    )
    
    output = result.stdout
    
    # Verifica SANs
    if "Subject Alternative Name" in output:
        san_section = output.split("Subject Alternative Name:")[1].split("\n")[0:3]
        print("✅ Subject Alternative Names (SANs) presentes:")
        print("\n".join(line.strip() for line in san_section if line.strip()))
    else:
        raise ValueError("❌ SANs não encontrados")

    # Verifica Key Usage
    if "Digital Signature" in output and "Key Encipherment" in output:
        print("✅ Key Usage correto (digitalSignature, keyEncipherment)")
    else:
        raise ValueError("❌ Key Usage incorreto")

    # Verifica Extended Key Usage
    if "TLS Web Server Authentication" in output:
        print("✅ Extended Key Usage correto (serverAuth)")
    else:
        raise ValueError("❌ Extended Key Usage incorreto")

def main():
    parser = argparse.ArgumentParser(description="Verify MQTT broker certificate")
    parser.add_argument("--cert", type=Path, default="certs/broker/broker.crt", 
                       help="Path to broker certificate")
    parser.add_argument("--ca", type=Path, default="certs/ca.crt", 
                       help="Path to CA certificate")
    args = parser.parse_args()

    try:
        verify_certificate(args.cert, args.ca)
    except Exception as e:
        print(f"❌ Erro na verificação: {str(e)}")

if __name__ == "__main__":
    main()