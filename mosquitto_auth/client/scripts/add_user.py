import argparse
import sys
from pathlib import Path
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager

def main():
    parser = argparse.ArgumentParser(description="Add a user to the Mosquitto password file")
    parser.add_argument("-f", "--file", type=Path, default=settings.PASSWD_FILE_PATH)
    parser.add_argument("-u", "--username", required=True, help="Username")
    parser.add_argument("-p", "--password", required=True, help="User password")
    parser.add_argument("-c", "--overwrite", action="store_true", help="Create new file (overwrite existing)")
    parser.add_argument("--hash-alg", default="sha512-pbkdf2", choices=MosquittoUserManager.HASH_ALGORITHMS)
    parser.add_argument("--no-reload", action="store_true", help="Do not reload Mosquitto after changes")
    
    args = parser.parse_args()
    manager = MosquittoUserManager(args.file, args.hash_alg)
    
    try:
        if not manager.add_user(args.username, args.password, args.overwrite):
            sys.exit(1)
            
        print(f"✅ User {args.username} added successfully")
            
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()