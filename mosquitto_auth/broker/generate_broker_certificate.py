import subprocess
import os
from pathlib import Path
import argparse
from mosquitto_auth.api.config import BROKER_CN

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

def main():
    parser = argparse.ArgumentParser(description="Generate MQTT broker certificate with SAN.")
    parser.add_argument("--cn", type=str, help="Common Name (IP or domain)", default=None)
    parser.add_argument("--days", type=int, default=365, help="Validity in days")
    parser.add_argument("--keep-temp", action="store_true", help="Manter arquivos temporários")
    args = parser.parse_args()

    # Usa BROKER_CN se --cn não for fornecido
    cn = args.cn if args.cn is not None else BROKER_CN
    if not cn:
        raise ValueError("Common Name (CN) não especificado e BROKER_CN não configurado")
    
    # Converte todos os caminhos para absolutos
    base_dir = Path(__file__).parent.parent.parent
    certs_dir = base_dir / "certs"
    broker_dir = certs_dir / "broker"
    broker_dir.mkdir(parents=True, exist_ok=True)

    ca_key = certs_dir / "ca.key"
    ca_crt = certs_dir / "ca.crt"
    validate_ca_files(ca_key, ca_crt)

    # Arquivos de certificado (caminhos absolutos)
    broker_key = broker_dir / "broker.key"
    broker_csr = broker_dir / "broker.csr"
    broker_crt = broker_dir / "broker.crt"
    openssl_cnf = broker_dir / "openssl.cnf"

    # Configuração SAN com caminhos absolutos no openssl.cnf
    openssl_cnf.write_text(f"""
[ ca ]
default_ca = CA_default

[ CA_default ]
dir = {broker_dir.as_posix()}
database = $dir/index.txt
new_certs_dir = $dir
certificate = {ca_crt.as_posix()}
private_key = {ca_key.as_posix()}
serial = $dir/serial
default_days = {args.days}
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
IP.1 = {cn}
IP.2 = 127.0.0.1
DNS.1 = localhost
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
    setup_ca_database(broker_dir)
    
    subprocess.run([
        "openssl", "ca", "-batch", "-in", str(broker_csr), 
        "-out", str(broker_crt), "-config", str(openssl_cnf),
        "-extensions", "v3_req", "-notext", "-md", "sha256"
    ], check=True, cwd=str(broker_dir))

    secure_permissions(broker_key, broker_crt)
    
    # Limpeza de arquivos temporários
    if not args.keep_temp:
        temp_files = [
            broker_csr,
            openssl_cnf,
            broker_dir / "index.txt",
            broker_dir / "index.txt.attr",
            broker_dir / "index.txt.old",
            broker_dir / "serial",
            broker_dir / "serial.old",
            broker_dir / "crlnumber",
            broker_dir / "01.pem"  
        ]
        cleanup_temp_files(*temp_files)
    
    print(f"""
✅ Certificado gerado com sucesso!
Arquivos:
- Chave privada: {broker_key}
- Certificado: {broker_crt}
SANs incluídos:
- IP: {cn}
- IP: 127.0.0.1
- DNS: localhost
""")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no OpenSSL: Verifique os arquivos de configuração")
        print(f"Detalhes: {e.stderr}")
    except Exception as e:
        print(f"❌ Erro crítico: {str(e)}")