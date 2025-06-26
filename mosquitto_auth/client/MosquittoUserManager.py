import os
import sys
import platform
import subprocess
import argparse
from typing import Optional, List, Tuple
from pathlib import Path
from mosquitto_auth.core.validators import validate_single_user
from mosquitto_auth.api.config import settings
from mosquitto_auth.core.utils import reload_mosquitto 

class MosquittoUserManager:
    """Classe principal para gerenciamento de usuários Mosquitto (não interativo)"""
    
    MOSQUITTO_PATHS = {
        'windows': 'C:\\Program Files\\mosquitto\\mosquitto_passwd.exe',
        'linux': '/usr/bin/mosquitto_passwd',
        'darwin': '/usr/local/bin/mosquitto_passwd'
    }
    
    HASH_ALGORITHMS = ['sha512-pbkdf2', 'sha512']
    
    def __init__(self, passwd_file: Path, hash_alg: str = 'sha512-pbkdf2'):
        self.passwd_file = passwd_file
        self.hash_alg = hash_alg
    
    def get_mosquitto_cmd(self) -> str:
        """Retorna o comando mosquitto_passwd correto para o OS"""
        system = platform.system().lower()
        path = self.MOSQUITTO_PATHS.get(system, self.MOSQUITTO_PATHS['linux'])
        
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"mosquitto_passwd não encontrado em: {path}\n"
                f"Instale o Mosquitto:\n"
                f"- Windows: https://mosquitto.org/download/\n"
                f"- Linux: sudo apt-get install mosquitto\n"
                f"- macOS: brew install mosquitto"
            )
        return path
    
    def execute_command(self, username: str, password: Optional[str] = None,
                       delete: bool = False, create: bool = False) -> bool:
        """Executa o comando mosquitto_passwd"""
        if self.hash_alg not in self.HASH_ALGORITHMS:
            raise ValueError(f"Algoritmo inválido. Use: {', '.join(self.HASH_ALGORITHMS)}")
        
        cmd = [self.get_mosquitto_cmd(), "-H", self.hash_alg]
        
        if delete:
            cmd.extend(["-D", str(self.passwd_file), username])
        elif create:
            cmd.extend(["-c", str(self.passwd_file), username])
        elif password:
            cmd.extend(["-b", str(self.passwd_file), username, password])
        else:
            raise ValueError("Senha obrigatória para operações de adição/atualização")

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar mosquitto_passwd: {e.stderr}", file=sys.stderr)
            return False
    
    def process_user(self, username: str, password: Optional[str] = None,
                    delete: bool = False, create: bool = False) -> Tuple[bool, str]:
        """Processa um único usuário SEM interação"""
        try:
            if delete:
                if password:
                    print("⚠️ Aviso: Senha ignorada para operação de remoção", file=sys.stderr)
                success = self.execute_command(username, delete=True)
                action = "removido"
            else:
                if not password:
                    raise ValueError("Senha obrigatória para operações de adição/atualização")
                
                valid_user, valid_pass = validate_single_user(username, password)
                success = self.execute_command(valid_user, valid_pass, create=create)
                action = "adicionado/atualizado"
            
            return success, action
        except ValueError as e:
            print(f"Erro de validação: {e}", file=sys.stderr)
            return False, ""
    
    def process_batch(self, user_list: List[Tuple[str, str]], create: bool = False) -> bool:
        """Processa múltiplos usuários em lote"""
        all_success = True
        for username, password in user_list:
            try:
                valid_user, valid_pass = validate_single_user(username, password)
                success = self.execute_command(valid_user, valid_pass, create=create)
                
                if success:
                    print(f"✓ Usuário {valid_user} processado")
                else:
                    print(f"✗ Falha ao processar {valid_user}", file=sys.stderr)
                    all_success = False
                
                create = False 
            except ValueError as e:
                print(f"✗ Erro no usuário {username}: {e}", file=sys.stderr)
                all_success = False
        
        return all_success


def parse_batch_input(batch_str: str) -> List[Tuple[str, str]]:
    """Parseia a string de entrada no formato batch"""
    user_list = []
    for pair in batch_str.split(','):
        if ':' not in pair:
            raise ValueError(f"Formato inválido no par: {pair}")
        username, password = pair.split(':', 1)
        user_list.append((username.strip(), password.strip()))
    return user_list


def main():
    """Função principal para execução direta"""
    parser = argparse.ArgumentParser(
        description="Gerenciamento NÃO INTERATIVO de usuários Mosquitto",
        epilog="""Exemplos:
  Adicionar usuário: edit_users_password.py -f passwd -u user1 -p senha
  Remover usuário:   edit_users_password.py -f passwd -u user1 -D
  Modo batch:        edit_users_password.py -f passwd -b "user1:senha1,user2:senha2"
  Criar arquivo:     edit_users_password.py -f passwd -u admin -p admin123 -c"""
    )
    
    parser.add_argument(
        "-f", "--file",
        type=Path,
        help="Caminho para o arquivo de senhas"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-u", "--username",
        help="Nome do usuário para operação única"
    )
    group.add_argument(
        "-b", "--batch",
        help="Modo batch (formato: user1:pass1,user2:pass2)"
    )
    
    parser.add_argument(
        "-p", "--password",
        help="Senha do usuário (obrigatória para adição/atualização)"
    )
    
    parser.add_argument(
        "-D", "--delete",
        action="store_true",
        help="Remover usuário ao invés de adicionar"
    )
    
    parser.add_argument(
        "-c", "--create",
        action="store_true",
        help="Criar novo arquivo (sobrescreve existente)"
    )
    
    parser.add_argument(
        "--hash-alg",
        default="sha512-pbkdf2",
        choices=MosquittoUserManager.HASH_ALGORITHMS,
        help="Algoritmo de hash (padrão: sha512-pbkdf2)"
    )
    
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Não recarregar configuração após alteração"
    )
    
    args = parser.parse_args()
    args.file = args.file or settings.PASSWD_FILE_PATH
        
    manager = MosquittoUserManager(args.file, args.hash_alg)
    
    try:
        if args.batch:
            user_list = parse_batch_input(args.batch)
            success = manager.process_batch(user_list, args.create)
            
            if not success:
                print("⚠️ Alguns usuários falharam ao processar", file=sys.stderr)
                sys.exit(1)
        
        else:
            success, action = manager.process_user(
                username=args.username,
                password=args.password,
                delete=args.delete,
                create=args.create
            )
            
            if not success:
                sys.exit(1)
            
            print(f"✓ Usuário {args.username} {action} com sucesso")
        
        if not args.no_reload and not reload_mosquitto():
            sys.exit(1)
            
    except Exception as e:
        print(f"⛔ Erro crítico: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
