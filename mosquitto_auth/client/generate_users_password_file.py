import os
import re
import subprocess
import platform
from dotenv import load_dotenv
from typing import Dict
from mosquitto_auth.core.validators import validate_single_user
from mosquitto_auth.api.config import settings
from mosquitto_auth.core.utils import reload_mosquitto 

MOSQUITTO_PASSWD_PATHS = {
    'windows': 'C:\\Program Files\\mosquitto\\mosquitto_passwd.exe',
    'linux': '/usr/bin/mosquitto_passwd',
}


def get_env_users() -> Dict[str, str]:
    """Retrieve and validate all users/passwords from .env with pattern USER_X/PASS_X"""
    users = {}
    pattern = re.compile(r'^USER_(\d+)$')

    for key, user in os.environ.items():
        if match := pattern.match(key):
            index = match.group(1)
            if password := os.getenv(f"PASS_{index}"):
                try:
                    valid_user, valid_pass = validate_single_user(user, password)
                    users[valid_user] = valid_pass
                except ValueError as e:
                    print(f"⚠️ Invalid user {key}: {e}")
                    continue

    if not users:
        raise ValueError("No valid users found in .env")
    
    return users

def get_mosquitto_passwd_cmd():
    """Return the appropriate mosquitto_passwd command based on the OS"""
    system = platform.system().lower()
    
    if system == 'windows':
        if not os.path.exists(MOSQUITTO_PASSWD_PATHS['windows']):
            raise FileNotFoundError(
                f"mosquitto_passwd file not found at: {MOSQUITTO_PASSWD_PATHS['windows']}\n"
                "Make sure Mosquitto is installed in the default location."
            )
        return MOSQUITTO_PASSWD_PATHS['windows']
    else:
        if not os.path.exists(MOSQUITTO_PASSWD_PATHS['linux']):
            raise FileNotFoundError(
                f"mosquitto_passwd not found at expected path: {MOSQUITTO_PASSWD_PATHS['linux']}\n"
                "Install Mosquitto using: sudo apt-get install mosquitto"
            )
        return MOSQUITTO_PASSWD_PATHS['linux']

def generate_password_file(users, passwd_file_path):
    """Generate the password file using mosquitto_passwd"""
    if os.path.exists(passwd_file_path):
        os.remove(passwd_file_path)

    mosquitto_cmd = get_mosquitto_passwd_cmd()
    overwrite = True

    for username, password in users.items():
        cmd = [mosquitto_cmd, "-b"]
        if overwrite:
            cmd.append("-c") 
            overwrite = False
        
        cmd.extend([passwd_file_path, username, password])
        
        subprocess.run(cmd, check=True)

def main():
    load_dotenv()
    passwd_file = settings.PASSWD_FILE_PATH
    
    try:
        users = get_env_users()
        if not users:
            print("⚠️ No users found in .env")
            return

        os.makedirs('config', exist_ok=True)

        generate_password_file(users, passwd_file)
        print(f"✓ File {passwd_file} successfully updated with {len(users)} user(s)!")
        print(f"✓ Detected OS: {platform.system()}")
        
        if not reload_mosquitto():
            print("⚠️ Falha ao recarregar o Mosquitto")

    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running mosquitto_passwd: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
