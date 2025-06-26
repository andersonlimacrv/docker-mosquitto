import subprocess

def reload_mosquitto(container_name="mosquitto") -> bool:
    """
    Envia o sinal SIGHUP para o processo do Mosquitto dentro do container Docker.
    """
    print(f"🔄 Recarregando Mosquitto no container '{container_name}'...")
    try:
        result = subprocess.run(
            ["docker", "exec", container_name, "pkill", "-HUP", "mosquitto"],
            check=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Mosquitto recarregado via SIGHUP.")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Erro ao tentar recarregar o Mosquitto:")
        print(e.stderr or str(e))
        return False
