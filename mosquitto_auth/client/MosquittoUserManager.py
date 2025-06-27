import os
import sys
import platform
import subprocess
from typing import List, Dict, Any
from pathlib import Path
from mosquitto_auth.core.validators import validate_single_user
from mosquitto_auth.api.config import settings

class MosquittoUserManager:
    MOSQUITTO_PATHS: Dict[str, str] = {
        'windows': 'C:\\Program Files\\mosquitto\\mosquitto_passwd.exe',
        'linux': '/usr/bin/mosquitto_passwd',
        'darwin': '/usr/local/bin/mosquitto_passwd'
    }
    
    HASH_ALGORITHMS = ['sha512-pbkdf2', 'sha512']
    
    def __init__(self, passwd_file: Path = settings.PASSWD_FILE_PATH, hash_alg: str = 'sha512-pbkdf2'):
        self.passwd_file = passwd_file
        self.hash_alg = hash_alg
    
    def get_mosquitto_cmd(self) -> str:
        system = platform.system().lower()
        path = self.MOSQUITTO_PATHS.get(system, self.MOSQUITTO_PATHS['linux'])
        if not os.path.exists(path):
            msg = (
                f"mosquitto_passwd not found at: {path}\n"
                "Install Mosquitto:\n"
                "- Windows: https://mosquitto.org/download/\n"
                "- Linux: sudo apt-get install mosquitto\n"
                "- macOS: brew install mosquitto"
            )
            print(msg, file=sys.stderr)
            raise FileNotFoundError(msg)
        return path
    
    def _execute_command(self, cmd_args: List[str]) -> None:
        try:
            subprocess.run(
                [self.get_mosquitto_cmd(), *cmd_args],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"✅ Command succeeded: {cmd_args}")
        except subprocess.CalledProcessError as e:
            err = e.stderr.strip() or e.stdout.strip() or str(e)
            print(f"❌ Error executing mosquitto_passwd: {err}", file=sys.stderr)
            raise RuntimeError(err)
    
    def add_user(self, username: str, password: str, overwrite_file: bool = False) -> None:
        valid_user, valid_pass = validate_single_user(username, password)
        if not overwrite_file and self.user_exists(valid_user):
            msg = f"User '{valid_user}' already exists."
            print(f"❌ {msg}", file=sys.stderr)
            raise ValueError(msg)
        
        cmd_args = ["-H", self.hash_alg, "-b"]
        if overwrite_file:
            cmd_args.append("-c")
        cmd_args += [str(self.passwd_file), valid_user, valid_pass]
        
        self._execute_command(cmd_args)
        print(f"✅ User '{valid_user}' added{' with overwrite' if overwrite_file else ''}.")
    
    def edit_password(self, username: str, new_password: str) -> None:
        if not self.user_exists(username):
            msg = f"User '{username}' does not exist."
            print(f"❌ {msg}", file=sys.stderr)
            raise ValueError(msg)
        
        valid_user, valid_pass = validate_single_user(username, new_password)
        cmd_args = ["-H", self.hash_alg, "-b", str(self.passwd_file), valid_user, valid_pass]
        
        self._execute_command(cmd_args)
        print(f"✅ Password for '{valid_user}' updated.")
    
    def delete_user(self, username: str) -> None:
        if not self.user_exists(username):
            msg = f"User '{username}' does not exist."
            print(f"❌ {msg}", file=sys.stderr)
            raise ValueError(msg)
        
        cmd_args = ["-H", self.hash_alg, "-D", str(self.passwd_file), username]
        
        self._execute_command(cmd_args)
        print(f"✅ User '{username}' deleted.")
    
    def add_many_users(self, users: Any, overwrite_file: bool = False) -> None:
        if isinstance(users, dict):
            items = list(users.items())
        else:
            items = [(u.username, u.password) for u in users]  
        
        if overwrite_file and self.passwd_file.exists():
            self.passwd_file.unlink()
            print("🗑️  Existing passwd file removed for overwrite.")
        
        errors = []
        for u, p in items:
            try:
                current_overwrite = overwrite_file and not self.passwd_file.exists()
                self.add_user(u, p, current_overwrite)
            except Exception as e:
                errors.append(f"{u}: {e}")
        
        if errors:
            msg = "Errors in bulk add: " + "; ".join(errors)
            print(f"❌ {msg}", file=sys.stderr)
            raise RuntimeError(msg)
        
        print(f"✅ Bulk operation completed for {len(items)} users.")
    
    def user_exists(self, username: str) -> bool:
        if not self.passwd_file.exists():
            return False
        with open(self.passwd_file, 'r') as f:
            for line in f:
                if line.startswith(username + ":"):
                    return True
        return False
