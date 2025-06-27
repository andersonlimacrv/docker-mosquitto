import argparse
import sys
from pathlib import Path
from mosquitto_auth.api.config import settings
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager

def parse_users(input_str: str) -> list[tuple[str, str]]:
    return [tuple(pair.split(':', 1)) for pair in input_str.split(',')]

def main():
    parser = argparse.ArgumentParser(description="Adiciona múltiplos usuários ao arquivo Mosquitto")
    parser.add_argument("-f", "--file", type=Path, default=settings.PASSWD_FILE_PATH)
    parser.add_argument("-u", "--users", required=True, help="Lista no formato user1:pass1,user2:pass2")
    parser.add_argument("-c", "--overwrite", action="store_true", help="Criar novo arquivo (sobrescreve existente)")
    parser.add_argument("--hash-alg", default="sha512-pbkdf2", choices=MosquittoUserManager.HASH_ALGORITHMS)
    parser.add_argument("--no-reload", action="store_true", help="Não recarregar o Mosquitto após alteração")
    
    args = parser.parse_args()
    manager = MosquittoUserManager(args.file, args.hash_alg)
    
    try:
        users = parse_users(args.users)
        if not manager.add_many_users(users, args.overwrite):
            sys.exit(1)
            
    except Exception as e:
        print(f"⛔ Erro crítico: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()