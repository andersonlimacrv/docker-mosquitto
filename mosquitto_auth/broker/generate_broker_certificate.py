import subprocess
import os
from pathlib import Path
import argparse
from mosquitto_auth.api.core.config import settings
import ipaddress

def validate_ca_files(ca_key: Path, ca_crt: Path):
    if not ca_key.exists() or not ca_crt.exists():
        raise FileNotFoundError("CA files not found. Generate CA first!")

def secure_permissions(*files: Path):
    for file in files:
        file.chmod(0o644)

def setup_ca_database(ca_dir: Path):
    """Cria estrutura mínima para openssl ca"""
    (ca_dir / "index.txt").touch()
    (ca_dir / "serial").write_text("01")
    (ca_dir / "crlnumber").write_text("01")

def cleanup_temp_files(*files: Path):
    """Remove arquivos temporários que não são mais necessários"""
    for file in files:
        try:
            if file.exists():
                file.unlink()
                print(f"🧹 Removido arquivo temporário: {file}")
        except Exception as e:
            print(f"⚠️ Não foi possível remover {file}: {str(e)}")

def generate_broker_certificate(cn: str = None, days: int = 365, keep_temp: bool = False, 
                               ca_key_path: str = None, ca_cert_path: str = None,
                               broker_dir: str = None):
    if not cn:
        cn = settings.BROKER_CN
    if not cn:
        raise ValueError("Common Name (CN) não especificado e BROKER_CN não configurado")
    
    if not ca_key_path:
        ca_key_path = settings.ca_key_path
    if not ca_cert_path:
        ca_cert_path = settings.ca_cert_path
    if not broker_dir:
        broker_dir = settings.broker_dir
    
    base_dir = Path(__file__).parent.parent.parent
    certs_dir = base_dir / "certs"
    broker_dir_path = base_dir / broker_dir
    broker_dir_path.mkdir(parents=True, exist_ok=True)

    ca_key = base_dir / ca_key_path
    ca_crt = base_dir / ca_cert_path
    validate_ca_files(ca_key, ca_crt)

    broker_key = base_dir / settings.broker_key_path
    broker_csr = broker_dir_path / "broker.csr"
    broker_crt = base_dir / settings.broker_cert_path
    openssl_cnf = broker_dir_path / "openssl.cnf"

    alt_names = ""
    try:
        ipaddress.ip_address(cn)
        alt_names += f"IP.1 = {cn}\n"
        alt_names += "IP.2 = 127.0.0.1\n"
        alt_names += "DNS.1 = localhost\n"
    except ValueError:
        alt_names += "IP.1 = 127.0.0.1\n"
        alt_names += f"DNS.1 = {cn}\n"
        alt_names += "DNS.2 = localhost\n"

    openssl_cnf.write_text(f"""
[ ca ]
default_ca = CA_default

[ CA_default ]
dir = {broker_dir_path.as_posix()}
database = $dir/index.txt
new_certs_dir = $dir
certificate = {ca_crt.as_posix()}
private_key = {ca_key.as_posix()}
serial = $dir/serial
default_days = {days}
default_md = sha256
policy = policy_anything

[ policy_anything ]
countryName = optional
stateOrProvinceName = optional
localityName = optional
organizationName = optional
organizationalUnitName = optional
commonName = supplied
emailAddress = optional

[ req ]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[ req_distinguished_name ]
CN = {cn}

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[ alt_names ]
{alt_names}
""")

    print("🔐 Generating private key...")
    subprocess.run([
        "openssl", "genrsa", "-out", str(broker_key), "2048"
    ], check=True)

    print("📄 Creating CSR...")
    subprocess.run([
        "openssl", "req", "-new", "-key", str(broker_key), 
        "-out", str(broker_csr), "-config", str(openssl_cnf)
    ], check=True)

    print("🏅 Signing certificate...")
    setup_ca_database(broker_dir_path)
    
    subprocess.run([
        "openssl", "ca", "-batch", "-in", str(broker_csr), 
        "-out", str(broker_crt), "-config", str(openssl_cnf),
        "-extensions", "v3_req", "-notext", "-md", "sha256"
    ], check=True, cwd=str(broker_dir_path))

    secure_permissions(broker_key, broker_crt)
    
    if not keep_temp:
        temp_files = [
            broker_csr,
            openssl_cnf,
            broker_dir_path / "index.txt",
            broker_dir_path / "index.txt.attr",
            broker_dir_path / "index.txt.old",
            broker_dir_path / "serial",
            broker_dir_path / "serial.old",
            broker_dir_path / "crlnumber",
            broker_dir_path / "01.pem"  
        ]
        cleanup_temp_files(*temp_files)
    
    print(f"""
✅ Certificado gerado com sucesso!
Arquivos:
- Chave privada: {broker_key}
- Certificado: {broker_crt}
SANs incluídos:
- CN: {cn}
- IP: 127.0.0.1
- DNS: localhost
""")
    return broker_crt, broker_key

def main():
    parser = argparse.ArgumentParser(description="Generate MQTT broker certificate with SAN.")
    parser.add_argument("--cn", type=str, help="Common Name (IP or domain)", default=None)
    parser.add_argument("--days", type=int, default=365, help="Validity in days")
    parser.add_argument("--keep-temp", action="store_true", help="Manter arquivos temporários")
    parser.add_argument("--ca-key", type=str, help="Path to CA private key", default=None)
    parser.add_argument("--ca-cert", type=str, help="Path to CA certificate", default=None)
    parser.add_argument("--broker-dir", type=str, help="Broker certificates directory", default=None)
    args = parser.parse_args()

    generate_broker_certificate(
        args.cn, args.days, args.keep_temp,
        args.ca_key, args.ca_cert, args.broker_dir
    )

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no OpenSSL: Verifique os arquivos de configuração")
        print(f"Detalhes: {e.stderr}")
    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")