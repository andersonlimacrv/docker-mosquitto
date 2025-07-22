import os
import re
import sys
import platform
from typing import Dict
from dotenv import load_dotenv
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.core.validators import validate_single_user
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager

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


def main():
    load_dotenv()
    
    try:
        passwd_file = settings.PASSWD_FILE_PATH
        passwd_file.parent.mkdir(parents=True, exist_ok=True)
        
        manager = MosquittoUserManager(passwd_file)
        users = get_env_users()
        
        if not users:
            print("⚠️ No users found in .env", file=sys.stderr)
            sys.exit(1)
        
        if not manager.add_many_users(users, overwrite_file=True):
            sys.exit(1)
            
        print(f"✅ File {passwd_file} successfully updated with {len(users)} user(s)!")
        print(f"✅ Detected OS: {platform.system()}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
