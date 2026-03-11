#!/usr/bin/env python3
"""
start_services.py

Uruchamia cały stos: Supabase + n8n + Caddy + Redis.
Wszystko w jednym projekcie Docker Compose ("localai").
"""

import os
import subprocess
import shutil
import argparse
import platform

def run_command(cmd, cwd=None):
    """Uruchom polecenie shell i wypisz je."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def run_command_silent(cmd):
    """Uruchom polecenie shell cicho, zwróć kod wyjścia."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout.strip()

def generate_caddy_bcrypt_hash():
    """
    Generuje hash bcrypt z DOCLING_BASIC_AUTH_PASS i zapisuje go
    do pliku caddy-addon/docling-auth.conf z literalnymi wartościami.
    Caddy nie obsługuje {$VAR} wewnątrz bloku basic_auth,
    więc używamy dynamicznie generowanego pliku importowanego przez Caddyfile.
    """
    username = os.environ.get("DOCLING_BASIC_AUTH_USER", "admin")
    password = os.environ.get("DOCLING_BASIC_AUTH_PASS")
    if not password:
        print("OSTRZEŻENIE: DOCLING_BASIC_AUTH_PASS nie jest ustawiony w .env. Basic Auth dla Doclinga będzie nieaktywny.")
        # Utwórz pusty plik - Caddyfile importuje go, ale nie będzie basic_auth
        auth_conf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caddy-addon", "docling-auth.caddyfile")
        with open(auth_conf, "w") as f:
            f.write("# Basic Auth wyłączony (brak DOCLING_BASIC_AUTH_PASS w .env)\n")
        return

    print("Generowanie hasha bcrypt dla Docling Basic Auth...")
    result = subprocess.run(
        ["docker", "run", "--rm", "caddy:2-alpine", "caddy", "hash-password", "--plaintext", password],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"BŁĄD: Nie udało się wygenerować hasha bcrypt: {result.stderr}")
        return

    bcrypt_hash = result.stdout.strip()

    # Zapisz caddy-addon/docling-auth.conf z literalnymi wartościami
    # (Caddy nie obsługuje {$VAR} wewnątrz bloku basic_auth)
    addon_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "caddy-addon")
    auth_conf = os.path.join(addon_dir, "docling-auth.caddyfile")
    with open(auth_conf, "w") as f:
        f.write(f"basic_auth /docs* {{\n")
        f.write(f"    {username} {bcrypt_hash}\n")
        f.write(f"}}\n")
        f.write(f"basic_auth /ui* {{\n")
        f.write(f"    {username} {bcrypt_hash}\n")
        f.write(f"}}\n")

    print(f"Plik caddy-addon/docling-auth.conf wygenerowany pomyślnie.")

def ensure_docker_networks():
    """Sprawdź i utwórz zewnętrzne sieci Docker, jeśli nie istnieją."""
    networks = ["caddy-net", "shared-infra"]
    for network in networks:
        returncode, _ = run_command_silent(["docker", "network", "inspect", network])
        if returncode != 0:
            print(f"Tworzenie sieci Docker: {network}...")
            run_command(["docker", "network", "create", "--driver", "bridge", network])
        else:
            print(f"Sieć Docker '{network}' już istnieje.")

def ensure_docker_volumes():
    """Sprawdź i utwórz zewnętrzne woluminy Docker, jeśli nie istnieją."""
    volumes = ["n8n_storage"]
    for volume in volumes:
        returncode, _ = run_command_silent(["docker", "volume", "inspect", volume])
        if returncode != 0:
            print(f"Tworzenie woluminu Docker: {volume}...")
            run_command(["docker", "volume", "create", volume])
        else:
            print(f"Wolumen Docker '{volume}' już istnieje.")

def clone_supabase_repo():
    """Sklonuj repozytorium Supabase za pomocą sparse checkout, jeśli jeszcze nie istnieje."""
    if not os.path.exists("supabase"):
        print("Klonowanie repozytorium Supabase...")
        run_command([
            "git", "clone", "--filter=blob:none", "--no-checkout",
            "https://github.com/supabase/supabase.git"
        ])
        os.chdir("supabase")
        run_command(["git", "sparse-checkout", "init", "--cone"])
        run_command(["git", "sparse-checkout", "set", "docker"])
        run_command(["git", "checkout", "master"])
        os.chdir("..")
    else:
        print("Repozytorium Supabase już istnieje, aktualizowanie...")
        os.chdir("supabase")
        run_command(["git", "pull"])
        os.chdir("..")

def fix_windows_line_endings():
    """Napraw końce linii CRLF w plikach konfiguracyjnych Supabase na Windows."""
    if platform.system() != "Windows":
        return
    
    pooler_path = os.path.join("supabase", "docker", "volumes", "pooler", "pooler.exs")
    if not os.path.exists(pooler_path):
        return
    
    print("Naprawianie końców linii Windows w pooler.exs...")
    try:
        with open(pooler_path, 'rb') as f:
            content = f.read()
        content = content.replace(b'\r\n', b'\n')
        with open(pooler_path, 'wb') as f:
            f.write(content)
        print("Naprawiono końce linii w pooler.exs")
    except Exception as e:
        print(f"Ostrzeżenie: Nie udało się naprawić końców linii w pooler.exs: {e}")

def prepare_supabase_env():
    """Skopiuj .env do .env w supabase/docker."""
    env_path = os.path.join("supabase", "docker", ".env")
    env_example_path = os.path.join(".env")
    print("Kopiowanie .env z katalogu głównego do supabase/docker...")
    shutil.copyfile(env_example_path, env_path)

def stop_existing_containers(profile=None):
    """Zatrzymaj wszystkie kontenery projektu localai."""
    print("Zatrzymywanie i usuwanie istniejących kontenerów dla projektu 'localai'...")
    cmd = ["docker", "compose", "-p", "localai"]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml", "down"])
    run_command(cmd)

def start_services(profile=None, environment=None, build=False):
    """Uruchom wszystkie usługi (Supabase + n8n + Caddy + Redis)."""
    print("Uruchamianie wszystkich usług...")
    cmd = ["docker", "compose", "-p", "localai"]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml"])
    if environment and environment == "private":
        cmd.extend(["-f", "docker-compose.override.private.yml"])
    if environment and environment == "public":
        cmd.extend(["-f", "docker-compose.override.public.yml",
                    "-f", "docker-compose.override.public.supabase.yml"])
    cmd.extend(["up", "-d"])
    if build:
        cmd.append("--build")
    run_command(cmd)

def main():
    parser = argparse.ArgumentParser(description='Uruchom lokalne usługi AI i Supabase.')
    parser.add_argument('--profile', choices=['cpu', 'gpu-nvidia', 'gpu-amd', 'none'], default='none',
                      help='Profil Docker Compose (domyślnie: none)')
    parser.add_argument('--environment', choices=['private', 'public'], default='private',
                      help='Środowisko Docker Compose (domyślnie: private)')
    parser.add_argument('--build', action='store_true',
                      help='Przebuduj obrazy Docker (np. po zmianie n8n.dockerfile)')
    args = parser.parse_args()

    # Wczytaj .env do zmiennych środowiskowych (dla generate_caddy_bcrypt_hash)
    env_file = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

    # Upewnij się, że sieci i woluminy zewnętrzne istnieją
    ensure_docker_networks()
    ensure_docker_volumes()

    clone_supabase_repo()
    fix_windows_line_endings()
    prepare_supabase_env()

    # Generuj hash bcrypt dla Docling Basic Auth (Caddy)
    generate_caddy_bcrypt_hash()

    stop_existing_containers(args.profile)

    # Uruchom wszystko jednym poleceniem
    # (depends_on w docker-compose.yml pilnuje kolejności startu)
    start_services(args.profile, args.environment, args.build)

if __name__ == "__main__":
    main()
