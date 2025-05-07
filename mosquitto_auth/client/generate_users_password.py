import os
import re
import subprocess
import platform
from dotenv import load_dotenv

# Path configuration for Windows
MOSQUITTO_PASSWD_WINDOWS = 'C:\\Program Files\\mosquitto\\mosquitto_passwd.exe'

def get_env_users():
    """Retrieve all users and passwords from the .env file with the pattern USER_X / PASS_X"""
    users = {}
    pattern = re.compile(r'^USER_(\d+)$')

    for key, user in os.environ.items():
        match = pattern.match(key)
        if match:
            index = match.group(1)
            password = os.getenv(f"PASS_{index}")
            if user and password:
                users[user] = password

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
        # For Linux and other OS, use the command from PATH
        try:
            subprocess.run(["mosquitto_passwd", "-h"], 
                         check=True, 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            return "mosquitto_passwd"
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise FileNotFoundError(
                "mosquitto_passwd command not found in PATH.\n"
                "Install Mosquitto using: sudo apt-get install mosquitto"
            )

def generate_password_file(users, passwd_file_path):
    """Generate the password file using mosquitto_passwd"""
    # Remove previous file if it exists
    if os.path.exists(passwd_file_path):
        os.remove(passwd_file_path)

    mosquitto_cmd = get_mosquitto_passwd_cmd()
    first_user = True

    for username, password in users.items():
        cmd = [mosquitto_cmd, "-b"]
        if first_user:
            cmd.append("-c")  # Create new file
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

        # Create config directory if it doesn't exist
        os.makedirs('config', exist_ok=True)

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
