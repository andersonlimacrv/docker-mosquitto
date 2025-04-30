import os
import re
import subprocess
import platform
from dotenv import load_dotenv

# Configuração do caminho para Windows
MOSQUITTO_PASSWD_WINDOWS = 'C:\\Program Files\\mosquitto\\mosquitto_passwd.exe'

def get_env_users():
    """Busca todos os usuários e senhas do .env com padrão USER_X / PASS_X"""
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
    """Retorna o comando apropriado de acordo com o sistema operacional"""
    system = platform.system().lower()
    
    if system == 'windows':
        if not os.path.exists(MOSQUITTO_PASSWD_WINDOWS):
            raise FileNotFoundError(
                f"Arquivo mosquitto_passwd não encontrado em: {MOSQUITTO_PASSWD_WINDOWS}\n"
                "Certifique-se de que o Mosquitto está instalado no local padrão."
            )
        return MOSQUITTO_PASSWD_WINDOWS
    else:
        # Para Linux e outros sistemas, usa o comando diretamente no PATH
        try:
            subprocess.run(["mosquitto_passwd", "-h"], 
                         check=True, 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL)
            return "mosquitto_passwd"
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise FileNotFoundError(
                "Comando mosquitto_passwd não encontrado no PATH.\n"
                "Instale o Mosquitto com: sudo apt-get install mosquitto"
            )

def generate_password_file(users, passwd_file_path):
    """Gera o arquivo de senhas usando mosquitto_passwd"""
    # Apaga o arquivo anterior, se existir
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
            print("⚠️ Nenhum usuário encontrado no .env")
            return

        # Cria diretório config se não existir
        os.makedirs('config', exist_ok=True)

        generate_password_file(users, passwd_file)
        print(f"✓ Arquivo {passwd_file} atualizado com sucesso com {len(users)} usuários!")
        print(f"✓ Sistema operacional detectado: {platform.system()}")
        
    except FileNotFoundError as e:
        print(f"❌ Erro: {str(e)}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar mosquitto_passwd: {str(e)}")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main()