import os
import re
import subprocess
import platform
from dotenv import load_dotenv
from typing import Dict
from mosquitto_auth.core.validators import validate_single_user

MOSQUITTO_PASSWD_WINDOWS = 'C:\\Program Files\\mosquitto\\mosquitto_passwd.exe'
MOSQUITTO_PASSWD_LINUX = '/usr/bin/mosquitto_passwd' 

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
        if not os.path.exists(MOSQUITTO_PASSWD_WINDOWS):
            raise FileNotFoundError(
                f"mosquitto_passwd file not found at: {MOSQUITTO_PASSWD_WINDOWS}\n"
                "Make sure Mosquitto is installed in the default location."
            )
        return MOSQUITTO_PASSWD_WINDOWS
    else:
        if not os.path.exists(MOSQUITTO_PASSWD_LINUX):
            raise FileNotFoundError(
                f"mosquitto_passwd not found at expected path: {MOSQUITTO_PASSWD_LINUX}\n"
                "Install Mosquitto using: sudo apt-get install mosquitto"
            )
        return MOSQUITTO_PASSWD_LINUX

def generate_password_file(users, passwd_file_path):
    """Generate the password file using mosquitto_passwd"""
    if os.path.exists(passwd_file_path):
        os.remove(passwd_file_path)

    mosquitto_cmd = get_mosquitto_passwd_cmd()
    first_user = True

    for username, password in users.items():
        cmd = [mosquitto_cmd, "-b"]
        if first_user:
            cmd.append("-c") 
            first_user = False
        
        cmd.extend([passwd_file_path, username, password])
        
        subprocess.run(cmd, check=True)

def main():
    load_dotenv()
    passwd_file = os.path.join('config', 'mosquitto.passwd')
    
    try:
        users = get_env_users()
        if not users:
            print("⚠️ No users found in .env")
            return

        os.makedirs('config', exist_ok=True)

        print(f"👥 Users: {users}")
        generate_password_file(users, passwd_file)
        print(f"✓ File {passwd_file} successfully updated with {len(users)} user(s)!")
        print(f"✓ Detected OS: {platform.system()}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {str(e)}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error while running mosquitto_passwd: {str(e)}")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()
