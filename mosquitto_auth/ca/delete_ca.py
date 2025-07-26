from pathlib import Path
from mosquitto_auth.api.core.config import settings

def delete_ca_files():
    base_dir = Path(__file__).resolve().parent.parent.parent
    ca_cert = base_dir / settings.ca_cert_path
    ca_key = base_dir / settings.ca_key_path

    print(f"🗂️  Diretório base: {base_dir}")
    print(f"📄 Certificado CA: {ca_cert}")
    print(f"🔑 Chave CA: {ca_key}")

    removed = False
    for f in [ca_cert, ca_key]:
        if f.exists():
            f.unlink()
            print(f"✅ Removido: {f}")
            removed = True
        else:
            print(f"⚠️  Arquivo não encontrado: {f}")

    if not removed:
        raise FileNotFoundError("Certificado CA e chave não encontrados.")
    

def main():
    try:
        delete_ca_files()
    except FileNotFoundError as e:
        print(f"❌ {e}")

if __name__ == "__main__":
    main()
