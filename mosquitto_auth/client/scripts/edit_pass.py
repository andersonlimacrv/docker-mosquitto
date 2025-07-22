import argparse
import sys
from pathlib import Path
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager

def main():
    parser = argparse.ArgumentParser(description="Altera a senha de um usuário Mosquitto")
    parser.add_argument("-f", "--file", type=Path, default=settings.PASSWD_FILE_PATH)
    parser.add_argument("-u", "--username", required=True, help="Nome do usuário")
    parser.add_argument("-p", "--password", required=True, help="Nova senha")
    parser.add_argument("--hash-alg", default="sha512-pbkdf2", choices=MosquittoUserManager.HASH_ALGORITHMS)
    parser.add_argument("--no-reload", action="store_true", help="Não recarregar o Mosquitto após alteração")
    
    args = parser.parse_args()
    manager = MosquittoUserManager(args.file, args.hash_alg)
    
    try:
        if not manager.edit_password(args.username, args.password):
            sys.exit(1)
            
        print(f"✅ Senha do usuário {args.username} alterada com sucesso")
            
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()