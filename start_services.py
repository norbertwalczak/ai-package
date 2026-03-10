#!/usr/bin/env python3
"""
start_services.py

Ten skrypt najpierw uruchamia stos Supabase, czeka na jego inicjalizację,
a następnie uruchamia lokalne usługi AI. Oba stosy używają tej samej
nazwy projektu Docker Compose ("localai"), dzięki czemu pojawiają się
razem w Docker Desktop.
"""

import os
import subprocess
import shutil
import time
import argparse
import platform
import sys

def run_command(cmd, cwd=None):
    """Uruchom polecenie shell i wypisz je."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

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
    print("Zatrzymywanie i usuwanie istniejących kontenerów dla projektu 'localai'...")
    cmd = ["docker", "compose", "-p", "localai"]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml", "down"])
    run_command(cmd)

def start_supabase(environment=None):
    """Uruchom usługi Supabase (używając ich pliku compose)."""
    print("Uruchamianie usług Supabase...")
    cmd = ["docker", "compose", "-p", "localai", "-f", "supabase/docker/docker-compose.yml",
           "-f", "docker-compose.override.supabase.yml"]
    if environment and environment == "public":
        cmd.extend(["-f", "docker-compose.override.public.supabase.yml"])
    cmd.extend(["up", "-d"])
    run_command(cmd)

def start_local_ai(profile=None, environment=None):
    """Uruchom lokalne usługi AI (używając pliku compose)."""
    print("Uruchamianie lokalnych usług AI...")
    cmd = ["docker", "compose", "-p", "localai"]
    if profile and profile != "none":
        cmd.extend(["--profile", profile])
    cmd.extend(["-f", "docker-compose.yml"])
    if environment and environment == "private":
        cmd.extend(["-f", "docker-compose.override.private.yml"])
    if environment and environment == "public":
        cmd.extend(["-f", "docker-compose.override.public.yml"])
    cmd.extend(["up", "-d"])
    run_command(cmd)

def main():
    parser = argparse.ArgumentParser(description='Uruchom lokalne usługi AI i Supabase.')
    parser.add_argument('--profile', choices=['cpu', 'gpu-nvidia', 'gpu-amd', 'none'], default='none',
                      help='Profil Docker Compose (domyślnie: none)')
    parser.add_argument('--environment', choices=['private', 'public'], default='private',
                      help='Środowisko Docker Compose (domyślnie: private)')
    args = parser.parse_args()

    clone_supabase_repo()
    fix_windows_line_endings()
    prepare_supabase_env()

    stop_existing_containers(args.profile)

    # Najpierw uruchom Supabase
    start_supabase(args.environment)

    # Daj Supabase czas na inicjalizację
    print("Oczekiwanie na inicjalizację Supabase...")
    time.sleep(10)

    # Następnie uruchom lokalne usługi AI
    start_local_ai(args.profile, args.environment)

if __name__ == "__main__":
    main()
