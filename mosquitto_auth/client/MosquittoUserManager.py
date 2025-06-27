import os
import sys
import platform
import subprocess
from typing import Optional, List, Tuple
from pathlib import Path
from mosquitto_auth.core.validators import validate_single_user
from mosquitto_auth.api.config import settings

class MosquittoUserManager:
    MOSQUITTO_PATHS = {
        'windows': 'C:\\Program Files\\mosquitto\\mosquitto_passwd.exe',
        'linux': '/usr/bin/mosquitto_passwd',
        'darwin': '/usr/local/bin/mosquitto_passwd'
    }
    
    HASH_ALGORITHMS = ['sha512-pbkdf2', 'sha512']
    
    def __init__(self, passwd_file: Path = settings.PASSWD_FILE_PATH, hash_alg: str = 'sha512-pbkdf2'):
        self.passwd_file = passwd_file
        self.hash_alg = hash_alg
    
    def get_mosquitto_cmd(self) -> str:
        """Retorna o caminho do executável mosquitto_passwd para o sistema"""
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
    
    def _execute_command(self, cmd_args: List[str]) -> bool:
        """Executa o comando mosquitto_passwd com os argumentos fornecidos"""
        try:
            subprocess.run(
                [self.get_mosquitto_cmd()] + cmd_args,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar mosquitto_passwd: {e.stderr}", file=sys.stderr)
            return False
    
    def add_user(self, username: str, password: str, overwrite_file: bool = False) -> bool:
        """
        Adiciona um novo usuário ao arquivo de senhas
        :param username: Nome do usuário
        :param password: Senha do usuário
        :param overwrite_file: Se True, cria um novo arquivo (sobrescreve existente)
        :return: True se bem-sucedido, False caso contrário
        """
        valid_user, valid_pass = validate_single_user(username, password)
        
        if not overwrite_file and self.user_exists(valid_user):
            print(f"Usuário {valid_user} já existe.", file=sys.stderr)
            return False
        
        cmd_args = ["-H", self.hash_alg, "-b"]
        
        if overwrite_file:
            cmd_args.append("-c")
        
        cmd_args.extend([str(self.passwd_file), valid_user, valid_pass])
        return self._execute_command(cmd_args)
    
    def edit_password(self, username: str, new_password: str) -> bool:
        """
        Altera a senha de um usuário existente
        :param username: Nome do usuário
        :param new_password: Nova senha
        :return: True se bem-sucedido, False caso contrário
        """
        if not self.user_exists(username):
            print(f"Usuário {username} não existe no arquivo", file=sys.stderr)
            return False
            
        valid_user, valid_pass = validate_single_user(username, new_password)
        cmd_args = ["-H", self.hash_alg, "-b", str(self.passwd_file), valid_user, valid_pass]
        return self._execute_command(cmd_args)
    
    def delete_user(self, username: str) -> bool:
        """
        Remove um usuário do arquivo de senhas
        :param username: Nome do usuário a ser removido
        :return: True se bem-sucedido, False caso contrário
        """
        if not self.user_exists(username):
            print(f"Usuário {username} não existe no arquivo", file=sys.stderr)
            return False
            
        cmd_args = ["-H", self.hash_alg, "-D", str(self.passwd_file), username]
        return self._execute_command(cmd_args)
    
    def add_many_users(self, users, overwrite_file: bool = False) -> bool:
        """
        Adiciona múltiplos usuários ao arquivo de senhas
        :param users: Lista de tuplas (username, password) OU dicionário {username: password}
        :param overwrite_file: Se True, cria um novo arquivo (sobrescreve existente)
        :return: True se todos forem bem-sucedidos, False caso contrário
        """
        all_success = True
        
        if isinstance(users, dict):
            users = list(users.items())
        
        # Se for para sobrescrever, remove o arquivo existente antes de começar
        if overwrite_file and self.passwd_file.exists():
            self.passwd_file.unlink()
        
        for username, password in users:
            try:
                valid_user, valid_pass = validate_single_user(username, password)
                
                # Apenas o primeiro usuário pode ter overwrite=True
                current_overwrite = overwrite_file and not self.passwd_file.exists()
                
                if not self.add_user(valid_user, valid_pass, current_overwrite):
                    print(f"❌ Falha ao adicionar usuário {valid_user}", file=sys.stderr)
                    all_success = False
                else:
                    print(f"✅ Usuário {valid_user} adicionado com sucesso")
            
            except ValueError as e:
                print(f"❌ Erro no usuário {username}: {e}", file=sys.stderr)
                all_success = False
        
        return all_success
    
    def user_exists(self, username: str) -> bool:
        """
        Verifica se um usuário existe no arquivo de senhas
        :param username: Nome do usuário a verificar
        :return: True se existe, False caso contrário
        """
        if not self.passwd_file.exists():
            return False
            
        with open(self.passwd_file, 'r') as f:
            for line in f:
                if line.startswith(username + ":"):
                    return True
        return False