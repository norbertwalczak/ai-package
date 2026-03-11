# CLAUDE.md

Ten plik zawiera wytyczne dla Claude Code (claude.ai/code) podczas pracy z kodem w tym repozytorium.

## Przegląd projektu

Samodzielnie hostowane środowisko deweloperskie AI oparte na Docker Compose, łączące n8n (automatyzacja low-code), Supabase (baza danych/uwierzytelnianie), Caddy (reverse proxy), Portainer (zarządzanie kontenerami) i Docling Serve (API konwersji dokumentów — PDF, DOCX, PPTX → Markdown/JSON dla RAG pipeline). Redis (Valkey) jest dostępny jako cache/kolejka.

## Komendy

### Uruchamianie usług
```bash
# Standardowe uruchomienie (lokalne)
# UWAGA: start_services.py automatycznie generuje hash bcrypt dla Docling Basic Auth
python3 start_services.py --profile none --environment private

# Z przebudową obrazu n8n (po zmianie n8n.dockerfile lub pakietów npm)
python3 start_services.py --profile none --environment private --build

# Wdrożenie produkcyjne (zamyka nieistotne porty)
python3 start_services.py --profile none --environment public
```

### Zatrzymywanie usług
```bash
docker compose -p localai -f docker-compose.yml down
```

### Aktualizacja kontenerów
```bash
docker compose -p localai -f docker-compose.yml down
docker compose -p localai -f docker-compose.yml pull
python3 start_services.py --profile none
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

- **start_services.py**: Główny punkt wejścia — klonuje repozytorium Supabase, tworzy sieci/woluminy, **generuje hash bcrypt dla Docling Basic Auth** i plik `caddy-addon/docling-auth.caddyfile`, uruchamia wszystkie usługi jednym poleceniem `docker compose up`
- **docker-compose.yml**: Główny plik compose z usługami n8n (main + worker), caddy, redis i docling-serve. Include Supabase ze zintegrowanym override. Używa kotwicy YAML `x-n8n` dla szablonu usługi. `depends_on` pilnuje kolejności startu (db, redis → n8n)
- **docker-compose.override.supabase.yml**: Nadpisanie Supabase — busybox stuby dla analytics/vector, sieci zewnętrzne dla serwisów
- **docker-compose.override.private.yml**: Udostępnia porty (np. 5678 dla n8n, 5001 dla docling-serve)
- **docker-compose.override.public.yml**: Zamyka porty, ruch tylko przez Caddy
- **supabase/**: Sparse checkout konfiguracji Docker Supabase (klonowane w czasie wykonywania)
- **migrate.py**: Skrypt migracji SQL — uruchamia pliki z `./migrations/` i opcjonalnie `./seeds/`
- **caddy-addon/docling-auth.caddyfile**: Generowany automatycznie przez `start_services.py` — zawiera `basic_auth` dla Docling `/docs` i `/ui` z literalnym hashem bcrypt

### Adresy URL usług (lokalne/prywatne)
- n8n: http://localhost:5678
- Supabase Studio (przez Kong): http://localhost:8000
- Portainer: http://localhost:9000
- Docling Serve API: http://localhost:5001
- Docling Serve UI: http://localhost:5001/ui
- Docling Serve Docs: http://localhost:5001/docs

### Kluczowa konfiguracja
- Wszystkie usługi współdzielą nazwę projektu `localai` dla ujednoliconego widoku w Docker Desktop
- n8n łączy się z Supabase Postgres pod hostem `db` (sieć `shared-infra`)
- Redis (Valkey) pod `redis:6379` (sieć `shared-infra`)
- Sieci zewnętrzne: `shared-infra` (inter-serwisowa), `caddy-net` (proxy)
- Współdzielony folder zamontowany pod `/data/shared` w kontenerze n8n
- Docling Serve: CPU-only (`DOCLING_DEVICE=cpu`), obraz `docling-serve-cpu`, n8n może wywoływać wewnętrznie pod `http://docling-serve:5001`
- Docling `entrypoint` pobiera brakujące modele HF (np. `CodeFormulaV2`) przed startem serwera — tylko przy pierwszym uruchomieniu
- Wolumin `docling-models` persystuje pobrane modele AI między restartami kontenera
- Basic Auth dla `/docs` i `/ui` Doclinga generowany przez `start_services.py` do `caddy-addon/docling-auth.caddyfile`

### Rekomendowana konfiguracja Docling dla RAG pipeline

Przy wywoływaniu API (`/v1/convert/source`) użyj następujących opcji:

| Opcja | Wartość | Powód |
|---|---|---|
| Format wyjściowy | `markdown` | Najlepszy dla chunkowania i wektoryzacji |
| Image Export Mode | `placeholder` | Nie osadza obrazów base64 — lżejsze chunki |
| Pipeline type | `standard` | Balans dokładność/szybkość na CPU |
| OCR Engine | `auto` | Docling sam dobiera silnik |
| PDF Backend | `docling_parse` | Lepiej rozumie układ tabel i kolumn |
| Table Mode | `accurate` | Poprawnie odczytuje złożone tabele |
| Enable formula enrichment | `true` | Wymaga modelu `CodeFormulaV2` (pobierany przy starcie) |
| Enable code enrichment | `true` | Oznacza bloki kodu w dokumentacji technicznej |
| Enable picture description | `false` | Zbyt wolne na CPU |

Przykład wywołania z n8n (HTTP Request node):
```json
{
  "sources": [{"kind": "file", "base64_data": "...", "filename": "dokument.pdf"}],
  "options": {
    "to_formats": ["markdown"],
    "image_export_mode": "placeholder",
    "pipeline_options": {
      "do_ocr": true,
      "do_table_structure": true,
      "table_structure_options": {"mode": "accurate"},
      "do_code_enrichment": true,
      "do_formula_enrichment": true,
      "do_picture_description": false
    }
  }
}
```

## Pliki workflow
- `n8n/backup/workflows/`: Workflow n8n do ręcznego importu
- `n8n_pipe.py`: Funkcja Open WebUI do integracji z n8n

## Migracje bazy danych

### Struktura katalogów
- `migrations/` — pliki SQL ze zmianami schematu (tabele, indeksy, RLS). Uruchamiane na każdym środowisku.
- `seeds/` — pliki SQL z danymi testowymi (mock). Uruchamiane **tylko lokalnie**.

### Konwencja nazewnictwa plików
Pliki numerowane trzycyfrowo, posortowane alfabetycznie:
```
migrations/001_create_schema.sql
migrations/002_create_tables.sql
seeds/001_mock_users.sql
```

### Zasady tworzenia plików SQL
- **Zawsze używaj `IF NOT EXISTS`** — migracje muszą być idempotentne (bezpieczne do wielokrotnego uruchomienia):
  ```sql
  CREATE SCHEMA IF NOT EXISTS app;
  CREATE TABLE IF NOT EXISTS app.products (...);
  ```
- **Jeden plik = jedna logiczna zmiana** (np. schemat, tabela, polityki RLS)
- **Nie usuwaj ani nie modyfikuj istniejących plików migracji** — dodawaj nowe z kolejnym numerem

### Uruchamianie migracji
```bash
python3 migrate.py                 # tylko migracje
python3 migrate.py --seed          # migracje + seedy
python3 migrate.py --seed-only     # tylko seedy
python3 migrate.py --dry-run       # podgląd co zostanie uruchomione
```

### Ważne
- Skrypt czyta `POSTGRES_USER` i `POSTGRES_DB` z `.env`
- Skrypt **nie śledzi** które migracje były już uruchomione — odpala wszystko od początku
- Na serwerze produkcyjnym uruchamiaj **bez** flagi `--seed`
- Na tym systemie polecenie Pythona to `python3`, **nie** `python`
