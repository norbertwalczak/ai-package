# Pakiet AI — n8n + Supabase

Samodzielnie hostowane środowisko deweloperskie oparte na Docker Compose, łączące **n8n** (automatyzacja low-code), **Supabase** (baza danych/uwierzytelnianie), **Caddy** (reverse proxy) i **Portainer** (zarządzanie kontenerami). **Redis (Valkey)** jest dostępny jako cache/kolejka dla n8n.

## Co jest zawarte

✅ [**n8n**](https://n8n.io/) — Platforma low-code z ponad 400 integracjami i zaawansowanymi komponentami AI (instancja main + worker w trybie queue)

✅ [**Supabase**](https://supabase.com/) — Open source baza danych jako usługa — PostgreSQL, uwierzytelnianie, storage, edge functions

✅ [**Caddy**](https://caddyserver.com/) — Automatyczny HTTPS/TLS reverse proxy dla niestandardowych domen

✅ [**Redis (Valkey)**](https://valkey.io/) — Cache i broker kolejki dla n8n queue mode

✅ [**Portainer**](https://www.portainer.io/) — Webowy panel zarządzania kontenerami Docker

✅ [**Docling Serve**](https://github.com/docling-project/docling-serve) — API konwersji dokumentów (PDF, DOCX, PPTX → Markdown/JSON) do budowy baz wiedzy RAG

## Wymagania wstępne

- [Python 3](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)
- [Docker / Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Instalacja

1. Sklonuj repozytorium:
   ```bash
   git clone <url-repozytorium>
   cd ai-package
   ```

2. Utwórz plik `.env` na podstawie `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Ustaw wymagane sekrety w `.env`:
   ```bash
   ############
   # Konfiguracja N8N
   ############
   N8N_ENCRYPTION_KEY=          # losowy ciąg znaków
   N8N_USER_MANAGEMENT_JWT_SECRET=  # losowy ciąg znaków

   ############
   # Sekrety Supabase
   ############
   POSTGRES_PASSWORD=           # silne hasło (bez znaku @!)
   JWT_SECRET=                  # min. 32 znaki
   ANON_KEY=                    # JWT anon key
   SERVICE_ROLE_KEY=            # JWT service role key
   DASHBOARD_USERNAME=          # login do Supabase Studio
   DASHBOARD_PASSWORD=          # hasło do Supabase Studio

   ############
   # Docling Serve
   ############
   DOCLING_API_KEY=             # klucz API — generuj: python3 -c "import secrets; print(secrets.token_hex(32))"
   DOCLING_BASIC_AUTH_USER=     # login Basic Auth dla /docs i /ui
   DOCLING_BASIC_AUTH_PASS=     # hasło Basic Auth (hash bcrypt generowany automatycznie)
   ```

> [!IMPORTANT]
> Generuj bezpieczne losowe wartości dla wszystkich sekretów. Nigdy nie używaj przykładowych wartości w produkcji.

4. Uruchom usługi:
   ```bash
   python3 start_services.py --profile none --environment private
   ```

## Komendy

### Uruchamianie usług

```bash
# Standardowe uruchomienie (lokalne)
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
python3 start_services.py --profile none --environment private
```

### Restart / przeładowanie Caddy

```bash
# Przeładowanie konfiguracji bez restartu (zero downtime)
docker exec caddy caddy reload --config /etc/caddy/Caddyfile

# Restart kontenera Caddy (jeśli reload nie wystarczy)
docker compose -p localai -f docker-compose.yml restart caddy
```

> **Uwaga:** Nie ma potrzeby uruchamiania `start_services.py` ani restartowania innych usług. Caddy działa niezależnie.

## Adresy URL usług (lokalne)

| Usługa | Adres |
|---|---|
| n8n | http://localhost:5678 |
| Supabase Studio (Kong) | http://localhost:8000 |
| Portainer | http://localhost:9000 |
| Docling Serve API | http://localhost:5001 |
| Docling Serve UI | http://localhost:5001/ui |
| Docling Serve Docs | http://localhost:5001/docs |

## Migracje bazy danych

Projekt używa numerowanych plików SQL do migracji schematu i danych testowych:

```
migrations/001_create_schema.sql    ← schemat, tabele, RLS (każde środowisko)
seeds/001_mock_data.sql             ← mock dane (tylko lokalnie)
```

```bash
python3 migrate.py                 # tylko migracje
python3 migrate.py --seed          # migracje + seedy
python3 migrate.py --seed-only     # tylko seedy
python3 migrate.py --dry-run       # podgląd co zostanie uruchomione
```

> [!WARNING]
> Na serwerze produkcyjnym uruchamiaj **bez** flagi `--seed`. Skrypt nie śledzi uruchomionych migracji — odpala wszystko od początku. Pliki SQL powinny być idempotentne (`IF NOT EXISTS`).

## Architektura

```
docker-compose.yml
  ├─ include (path lista):
  │   ├─ supabase/docker/docker-compose.yml  ← bazowy Supabase
  │   └─ docker-compose.override.supabase.yml ← busybox stuby + sieci + mail config
  ├─ n8n-main (depends_on: db, redis)
  ├─ n8n-worker (queue mode)
  ├─ caddy (reverse proxy)
  ├─ redis (Valkey — cache/kolejka)
  └─ docling-serve (API konwersji dokumentów)
```

| Plik | Opis |
|---|---|
| `start_services.py` | Punkt wejścia — klonuje Supabase, tworzy sieci/woluminy, generuje Basic Auth hash, uruchamia stos |
| `docker-compose.yml` | Główny compose — n8n, caddy, redis, docling-serve + include Supabase |
| `docker-compose.override.supabase.yml` | Busybox stuby (analytics/vector), sieci, konfiguracja maili auth |
| `docker-compose.override.private.yml` | Otwarte porty (dev), w tym port 5001 dla Docling |
| `docker-compose.override.public.yml` | Zamknięte porty (produkcja, ruch przez Caddy) |
| `n8n.dockerfile` | Customowy obraz n8n z dodatkowymi pakietami npm |
| `migrate.py` | Skrypt migracji SQL |
| `Caddyfile` | Konfiguracja reverse proxy (Basic Auth dla Docling /docs i /ui) |
| `caddy-addon/docling-auth.caddyfile` | Generowany automatycznie — Basic Auth dla Docling (username + hash bcrypt) |

### Sieci

- **shared-infra** — komunikacja między n8n, Supabase i Redis
- **caddy-net** — komunikacja Caddy ↔ n8n, Kong, Studio

### Kluczowa konfiguracja

- Projekt Docker: `localai`
- n8n → Postgres: host `db` (sieć `shared-infra`)
- n8n → Redis: host `redis:6379` (sieć `shared-infra`)
- n8n → Docling: `http://docling-serve:5001` (sieć `shared-infra`, wymagany nagłówek `X-Api-Key`)
- Wolumen `n8n_storage` (external) — dane n8n
- Wolumen `docling-models` — modele AI Docling (persystują między restartami)
- Katalog `./shared` zamontowany pod `/data/shared` w kontenerze n8n

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

## Wdrażanie w chmurze

1. Otwórz porty 80 i 443:
   ```bash
   ufw enable && ufw allow 80 && ufw allow 443 && ufw reload
   ```

2. Ustaw zmienne Caddy i Docling w `.env`:
   ```bash
   N8N_HOSTNAME=n8n.twojadomena.com
   SUPABASE_HOSTNAME=supabase.twojadomena.com
   PORTAINER_HOSTNAME=portainer.twojadomena.com
   DOCLING_HOSTNAME=docling.twojadomena.com
   LETSENCRYPT_EMAIL=twoj@email.com
   ```

3. Uruchom z profilem `public`:
   ```bash
   python3 start_services.py --profile none --environment public
   ```

4. Skonfiguruj rekordy DNS A: subdomeny → IP serwera.

## Importowanie workflow n8n

Gotowe workflow znajdują się w `n8n/backup/workflows/`:

1. Otwórz n8n: http://localhost:5678
2. **Importuj z pliku** → wybierz JSON z `n8n/backup/workflows/`
3. Utwórz credentials (Postgres host: `db`, Redis: `redis:6379`)

## Rozwiązywanie problemów

- **Supabase Pooler restartuje się** — zobacz [fix na GitHub](https://github.com/supabase/supabase/issues/30210#issuecomment-2456955578)
- **Supabase niedostępny** — upewnij się, że nie masz `@` w haśle Postgres
- **Brak plików w folderze Supabase** — usuń folder `supabase/` i uruchom ponownie `start_services.py`
- **Docker Desktop** — włącz „Expose daemon on tcp://localhost:2375 without TLS"

## Ważne

- Polecenie Pythona to `python3`, **nie** `python`
- Flaga `--build` jest potrzebna tylko po zmianie `n8n.dockerfile` lub pakietów npm

## 📜 Licencja

Projekt objęty licencją Apache License 2.0 — szczegóły w pliku [LICENSE](LICENSE).
