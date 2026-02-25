import argparse
import sys
from pathlib import Path
from mosquitto_auth.api.core.config import settings
from mosquitto_auth.client.MosquittoUserManager import MosquittoUserManager

def main():
    parser = argparse.ArgumentParser(description="Remove a user from the Mosquitto password file")
    parser.add_argument("-f", "--file", type=Path, default=settings.PASSWD_FILE_PATH)
    parser.add_argument("-u", "--username", required=True, help="Username to remove")
    parser.add_argument("--no-reload", action="store_true", help="Do not reload Mosquitto after changes")
    
    args = parser.parse_args()
    manager = MosquittoUserManager(args.file)
    
    try:
        if not manager.delete_user(args.username):
            sys.exit(1)
            
        print(f"✅ User {args.username} removed successfully")
            
    except Exception as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()