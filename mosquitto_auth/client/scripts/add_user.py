
import argparse
import sys
from pathlib import Path
from mosquitto_auth.api.config import settings
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager

def main():
    parser = argparse.ArgumentParser(description="Adiciona um usuário ao arquivo de senhas Mosquitto")
    parser.add_argument("-f", "--file", type=Path, default=settings.PASSWD_FILE_PATH)
    parser.add_argument("-u", "--username", required=True, help="Nome do usuário")
    parser.add_argument("-p", "--password", required=True, help="Senha do usuário")
    parser.add_argument("-c", "--overwrite", action="store_true", help="Criar novo arquivo (sobrescreve existente)")
    parser.add_argument("--hash-alg", default="sha512-pbkdf2", choices=MosquittoUserManager.HASH_ALGORITHMS)
    parser.add_argument("--no-reload", action="store_true", help="Não recarregar o Mosquitto após alteração")
    
    args = parser.parse_args()
    manager = MosquittoUserManager(args.file, args.hash_alg)
    
    try:
        if not manager.add_user(args.username, args.password, args.overwrite):
            sys.exit(1)
            
        print(f"✅ Usuário {args.username} adicionado com sucesso")
            
    except Exception as e:
        print(f"⛔ Erro crítico: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()