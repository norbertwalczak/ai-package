# GEMINI.md

Ten plik zawiera wytyczne dla Agenta podczas pracy z kodem w tym repozytorium.

## Przegląd projektu

Samodzielnie hostowane środowisko deweloperskie AI oparte na Docker Compose, łączące n8n (automatyzacja low-code), Supabase (baza danych/uwierzytelnianie) i Caddy (reverse proxy). Redis (Valkey) jest dostępny jako cache/kolejka.

## Komendy

### Uruchamianie usług
```bash
# Standardowe uruchomienie (bez Ollama)
python start_services.py --profile none

# Wdrożenie produkcyjne (zamyka nieistotne porty)
python start_services.py --profile none --environment public
```

### Zatrzymywanie usług
```bash
docker compose -p localai -f docker-compose.yml down
```

### Aktualizacja kontenerów
```bash
docker compose -p localai -f docker-compose.yml down
docker compose -p localai -f docker-compose.yml pull
python start_services.py --profile none
```

### Restart / przeładowanie Caddy (np. po zmianach w Caddyfile)
```bash
# Przeładowanie konfiguracji bez restartu (zero downtime)
docker exec caddy caddy reload --config /etc/caddy/Caddyfile

# Restart kontenera Caddy (jeśli reload nie wystarczy)
docker compose -p localai -f docker-compose.yml restart caddy
```
> **Uwaga:** Nie ma potrzeby uruchamiania `start_services.py` ani restartowania innych usług. Caddy działa niezależnie.

## Architektura

- **start_services.py**: Główny punkt wejścia — klonuje repozytorium Supabase, kopiuje .env, uruchamia najpierw Supabase, czeka 10 sekund, a następnie uruchamia lokalne usługi
- **docker-compose.yml**: Główny plik compose z usługami n8n, caddy i redis. Zawiera plik compose Supabase. Używa kotwicy YAML `x-n8n` dla szablonu usługi
- **docker-compose.override.*.yml**: Nadpisania specyficzne dla środowiska (private udostępnia porty, public je zamyka)
- **supabase/**: Sparse checkout konfiguracji Docker Supabase (klonowane w czasie wykonywania)

### Adresy URL usług (lokalne/prywatne)
- n8n: http://localhost:5678 (przez Caddy :8001)
- Supabase: (przez Caddy :8005)

### Kluczowa konfiguracja
- Wszystkie usługi współdzielą nazwę projektu `localai` dla ujednoliconego widoku w Docker Desktop
- n8n łączy się z Supabase Postgres pod hostem `db`
- Redis (Valkey) pod `redis:6379`
- Współdzielony folder zamontowany pod `/data/shared` w kontenerze n8n

## Pliki workflow
- `n8n/backup/workflows/`: Workflow n8n do ręcznego importu
- `n8n_pipe.py`: Funkcja Open WebUI do integracji z n8n
