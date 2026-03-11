#!/usr/bin/env python3
"""
migrate.py

Skrypt do uruchamiania migracji SQL i opcjonalnie seedów.
Migracje są uruchamiane w kolejności numerycznej z katalogu ./migrations/.
Seedy (mock dane) z katalogu ./seeds/ są uruchamiane tylko z flagą --seed.

Użycie:
    python3 migrate.py                 # tylko migracje
    python3 migrate.py --seed          # migracje + seedy
    python3 migrate.py --seed-only     # tylko seedy (bez migracji)
    python3 migrate.py --dry-run       # pokaż co zostanie uruchomione
"""

import os
import sys
import glob
import subprocess
import argparse


CONTAINER = "supabase-db"


def load_env(filepath=".env"):
    """Wczytaj zmienne z pliku .env (proste parsowanie key=value)."""
    env = {}
    if not os.path.isfile(filepath):
        return env
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def get_db_config():
    """Pobierz konfigurację bazy z .env."""
    env = load_env()
    return {
        "user": env.get("POSTGRES_USER", "postgres"),
        "db": env.get("POSTGRES_DB", "postgres"),
    }


def get_sql_files(directory):
    """Pobierz posortowane pliki .sql z katalogu."""
    if not os.path.isdir(directory):
        return []
    files = sorted(glob.glob(os.path.join(directory, "*.sql")))
    return files


def run_sql_file(filepath, db_config):
    """Uruchom plik SQL w kontenerze Postgres."""
    filename = os.path.basename(filepath)
    print(f"  ▶ {filename}...", end=" ", flush=True)
    
    with open(filepath, "r") as f:
        sql = f.read()

    result = subprocess.run(
        ["docker", "exec", "-i", CONTAINER, "psql",
         "-U", db_config["user"], "-d", db_config["db"],
         "-v", "ON_ERROR_STOP=1"],
        input=sql,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print("❌")
        print(f"    Błąd: {result.stderr.strip()}")
        return False
    else:
        print("✅")
        return True


def check_container():
    """Sprawdź czy kontener Postgres działa."""
    result = subprocess.run(
        ["docker", "inspect", CONTAINER, "--format", "{{.State.Status}}"],
        capture_output=True, text=True
    )
    if result.returncode != 0 or result.stdout.strip() != "running":
        print(f"❌ Kontener '{CONTAINER}' nie działa. Uruchom najpierw stack:")
        print(f"   python3 start_services.py --profile none --environment private")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Uruchom migracje SQL i seedy.")
    parser.add_argument("--seed", action="store_true",
                        help="Uruchom migracje + seedy (mock dane)")
    parser.add_argument("--seed-only", action="store_true",
                        help="Uruchom tylko seedy (bez migracji)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Pokaż pliki do uruchomienia bez wykonywania")
    args = parser.parse_args()

    check_container()

    migrations = get_sql_files("./migrations")
    seeds = get_sql_files("./seeds")

    run_migrations = not args.seed_only
    run_seeds = args.seed or args.seed_only

    if args.dry_run:
        if run_migrations:
            print(f"Migracje ({len(migrations)}):")
            for f in migrations:
                print(f"  - {os.path.basename(f)}")
            if not migrations:
                print("  (brak plików)")
        if run_seeds:
            print(f"Seedy ({len(seeds)}):")
            for f in seeds:
                print(f"  - {os.path.basename(f)}")
            if not seeds:
                print("  (brak plików)")
        return

    errors = 0
    db_config = get_db_config()
    print(f"🔧 Baza: {db_config['db']} | User: {db_config['user']}")

    if run_migrations:
        if migrations:
            print(f"\n📦 Migracje ({len(migrations)} plików):")
            for f in migrations:
                if not run_sql_file(f, db_config):
                    errors += 1
                    print("    ⛔ Przerywam migracje po błędzie.")
                    break
        else:
            print("\n📦 Brak plików migracji w ./migrations/")

    if run_seeds:
        if seeds:
            print(f"\n🌱 Seedy ({len(seeds)} plików):")
            for f in seeds:
                if not run_sql_file(f, db_config):
                    errors += 1
        else:
            print("\n🌱 Brak plików seedów w ./seeds/")

    if errors:
        print(f"\n⚠️  Zakończono z {errors} błędem/ami.")
        sys.exit(1)
    else:
        print("\n✅ Wszystko wykonane pomyślnie.")


if __name__ == "__main__":
    main()
