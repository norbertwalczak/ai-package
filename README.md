# Samodzielnie hostowany pakiet AI

**Samodzielnie hostowany pakiet AI** to otwarty szablon docker compose, który
szybko uruchamia w pełni funkcjonalne lokalne środowisko deweloperskie AI i Low Code,
zawierające Ollama do lokalnych modeli LLM, Open WebUI jako interfejs do rozmów z agentami N8N
oraz Supabase do bazy danych, magazynu wektorów i uwierzytelniania.

To jest wersja Cole'a z kilkoma ulepszeniami i dodatkiem Supabase, Open WebUI, Flowise, Neo4j, Langfuse, SearXNG i Caddy!
Gotowe workflow agentów RAG AI z filmu znajdują się w `n8n/backup/workflows/` — zobacz [Importowanie startowych workflow](#importowanie-startowych-workflow) po instrukcje konfiguracji.

**WAŻNE**: Supabase zaktualizował kilka zmiennych środowiskowych, więc może być konieczne dodanie nowych domyślnych wartości w pliku .env, które mam w swoim .env.example, jeśli już wcześniej uruchomiłeś ten projekt i teraz tylko pobierasz nowe zmiany. Konkretnie, musisz dodać „POOLER_DB_POOL_SIZE=5" do swojego .env. Jest to wymagane, jeśli uruchamiałeś pakiet przed 14 czerwca.

**Aktualizacja z 26 lutego 2026**: Najnowszy kontener Supabase storage (`storage-api v1.37.8`) wymaga teraz kilku nowych zmiennych środowiskowych. Jeśli już uruchamiałeś Lokalny Pakiet AI i pobierasz nowe zmiany, musisz dodać następujące wpisy do pliku `.env`:
```bash
GLOBAL_S3_BUCKET=stub
REGION=stub
STORAGE_TENANT_ID=stub
S3_PROTOCOL_ACCESS_KEY_ID=625729a08b95bf1b7ff351a663f3a23c
S3_PROTOCOL_ACCESS_KEY_SECRET=850181e4652dd023b7a98c58ae0d2d34bd487ee0cc3254aed6eda37307425907
```
Są one już zawarte w `.env.example`, więc jeśli konfigurujesz je po raz pierwszy, wystarczy je skopiować. Wartości `stub` działają prawidłowo w przypadku lokalnego przechowywania plików. Bez tych zmiennych kontener Supabase storage ulegnie awarii przy starcie z błędem „Region is missing".

## Ważne linki

- [Społeczność Local AI](https://thinktank.ottomator.ai/c/local-ai/18) na forum oTTomator Think Tank

- [Tablica Kanban na GitHub](https://github.com/users/coleam00/projects/2/views/1) do implementacji funkcji i naprawiania błędów.

- [Oryginalny Local AI Starter Kit](https://github.com/n8n-io/self-hosted-ai-starter-kit) od zespołu n8n

- Pobierz moją integrację N8N + OpenWebUI [bezpośrednio ze strony Open WebUI.](https://openwebui.com/f/coleam/n8n_pipe/) (więcej instrukcji poniżej)

![n8n.io - Zrzut ekranu](https://raw.githubusercontent.com/n8n-io/self-hosted-ai-starter-kit/main/assets/n8n-demo.gif)

Przygotowany przez <https://github.com/n8n-io> i <https://github.com/coleam00>, łączy samodzielnie hostowaną platformę n8n
z wyselekcjonowaną listą kompatybilnych produktów i komponentów AI, aby
szybko rozpocząć budowanie samodzielnie hostowanych workflow AI.

### Co jest zawarte

✅ [**Samodzielnie hostowany n8n**](https://n8n.io/) - Platforma low-code z ponad 400
integracjami i zaawansowanymi komponentami AI

✅ [**Supabase**](https://supabase.com/) - Open source baza danych jako usługa -
najczęściej używana baza danych dla agentów AI

✅ [**Ollama**](https://ollama.com/) - Wieloplatformowa platforma LLM do instalacji
i uruchamiania najnowszych lokalnych modeli LLM

✅ [**Open WebUI**](https://openwebui.com/) - Interfejs podobny do ChatGPT do
prywatnej interakcji z lokalnymi modelami i agentami N8N

✅ [**Flowise**](https://flowiseai.com/) - No/low code kreator agentów AI,
który doskonale współpracuje z n8n

✅ [**Qdrant**](https://qdrant.tech/) - Open source, wysokowydajny magazyn
wektorów z kompleksowym API. Mimo że można używać Supabase do RAG, ten został
zachowany (w przeciwieństwie do Postgres), ponieważ jest szybszy od Supabase, więc czasem jest lepszą opcją.

✅ [**Neo4j**](https://neo4j.com/) - Silnik grafów wiedzy, który zasila narzędzia takie jak GraphRAG, LightRAG i Graphiti

✅ [**SearXNG**](https://searxng.org/) - Open source, darmowy meta-silnik wyszukiwania internetowego, który agreguje
wyniki z nawet 229 usług wyszukiwania. Użytkownicy nie są śledzeni ani profilowani, stąd dopasowanie do lokalnego pakietu AI.

✅ [**Caddy**](https://caddyserver.com/) - Zarządzany HTTPS/TLS dla niestandardowych domen

✅ [**Langfuse**](https://langfuse.com/) - Open source platforma inżynierii LLM do obserwacji agentów

## Wymagania wstępne

Zanim zaczniesz, upewnij się, że masz zainstalowane następujące oprogramowanie:

- [Python](https://www.python.org/downloads/) - Wymagany do uruchomienia skryptu konfiguracyjnego
- [Git/GitHub Desktop](https://desktop.github.com/) - Do łatwego zarządzania repozytorium
- [Docker/Docker Desktop](https://www.docker.com/products/docker-desktop/) - Wymagany do uruchomienia wszystkich usług

## Instalacja

Sklonuj repozytorium i przejdź do katalogu projektu:
```bash
git clone -b stable https://github.com/coleam00/local-ai-packaged.git
cd local-ai-packaged
```

Przed uruchomieniem usług musisz skonfigurować zmienne środowiskowe dla Supabase zgodnie z ich [przewodnikiem po self-hostingu](https://supabase.com/docs/guides/self-hosting/docker#securing-your-services).

1. Utwórz kopię `.env.example` i zmień jej nazwę na `.env` w katalogu głównym projektu
2. Ustaw następujące wymagane zmienne środowiskowe:
   ```bash
   ############
   # Konfiguracja N8N
   ############
   N8N_ENCRYPTION_KEY=
   N8N_USER_MANAGEMENT_JWT_SECRET=

   ############
   # Sekrety Supabase
   ############
   POSTGRES_PASSWORD=
   JWT_SECRET=
   ANON_KEY=
   SERVICE_ROLE_KEY=
   DASHBOARD_USERNAME=
   DASHBOARD_PASSWORD=
   POOLER_TENANT_ID=

   ############
   # Sekrety Neo4j
   ############   
   NEO4J_AUTH=

   ############
   # Dane logowania Langfuse
   ############

   CLICKHOUSE_PASSWORD=
   MINIO_ROOT_PASSWORD=
   LANGFUSE_SALT=
   NEXTAUTH_SECRET=
   ENCRYPTION_KEY=  
   ```

> [!IMPORTANT]
> Upewnij się, że generujesz bezpieczne losowe wartości dla wszystkich sekretów. Nigdy nie używaj przykładowych wartości w produkcji.

3. Ustaw następujące zmienne środowiskowe, jeśli wdrażasz na produkcję, w przeciwnym razie pozostaw zakomentowane:
   ```bash
   ############
   # Konfiguracja Caddy
   ############

   N8N_HOSTNAME=n8n.twojadomena.com
   WEBUI_HOSTNAME=:openwebui.twojadomena.com
   FLOWISE_HOSTNAME=:flowise.twojadomena.com
   SUPABASE_HOSTNAME=:supabase.twojadomena.com
   OLLAMA_HOSTNAME=:ollama.twojadomena.com
   SEARXNG_HOSTNAME=searxng.twojadomena.com
   NEO4J_HOSTNAME=neo4j.twojadomena.com
   LETSENCRYPT_EMAIL=twoj-adres-email
   ```   

---

Projekt zawiera skrypt `start_services.py`, który obsługuje uruchamianie zarówno Supabase, jak i lokalnych usług AI. Skrypt przyjmuje flagę `--profile` do określenia konfiguracji GPU.

### Dla użytkowników GPU Nvidia

```bash
python start_services.py --profile gpu-nvidia
```

> [!NOTE]
> Jeśli nie używałeś jeszcze GPU Nvidia z Dockerem, postępuj zgodnie z
> [instrukcjami Ollama Docker](https://github.com/ollama/ollama/blob/main/docs/docker.mdx).

### Dla użytkowników GPU AMD na Linuxie

```bash
python start_services.py --profile gpu-amd
```

### Dla użytkowników Mac / Apple Silicon

Jeśli używasz Maca z procesorem M1 lub nowszym, niestety nie możesz udostępnić GPU instancji Dockera. W tym przypadku są dwie opcje:

1. Uruchom starter kit w pełni na CPU:
   ```bash
   python start_services.py --profile cpu
   ```

2. Uruchom Ollama na Macu dla szybszej inferencji i połącz się z nią z instancji n8n:
   ```bash
   python start_services.py --profile none
   ```

   Jeśli chcesz uruchomić Ollama na Macu, sprawdź [stronę główną Ollama](https://ollama.com/) po instrukcje instalacji.

#### Dla użytkowników Mac uruchamiających OLLAMA lokalnie

Jeśli uruchamiasz OLLAMA lokalnie na Macu (nie w Dockerze), musisz zmodyfikować zmienną środowiskową OLLAMA_HOST w konfiguracji usługi n8n. Zaktualizuj sekcję x-n8n w pliku Docker Compose w następujący sposób:

```yaml
x-n8n: &service-n8n
  # ... inne konfiguracje ...
  environment:
    # ... inne zmienne środowiskowe ...
    - OLLAMA_HOST=host.docker.internal:11434
```

Dodatkowo, po zobaczeniu „Editor is now accessible via: http://localhost:5678/":

1. Przejdź do http://localhost:5678/home/credentials
2. Kliknij „Local Ollama service"
3. Zmień bazowy URL na „http://host.docker.internal:11434/"

### Dla wszystkich pozostałych

```bash
python start_services.py --profile cpu
```

### Argument środowiska
Skrypt **start-services.py** oferuje możliwość przekazania jednej z dwóch opcji argumentu środowiska, **private** (domyślne środowisko) i **public**:
- **private:** wdrażasz stos w bezpiecznym środowisku, więc wiele portów może być dostępnych bez obaw o bezpieczeństwo
- **public:** stos jest wdrożony w publicznym środowisku, co oznacza, że powierzchnia ataku powinna być jak najmniejsza. Wszystkie porty oprócz 80 i 443 są zamknięte

Stos zainicjowany z
```bash
   python start_services.py --profile gpu-nvidia --environment private
   ```
jest równoważny temu zainicjowanemu z
```bash
   python start_services.py --profile gpu-nvidia
   ```

## Wdrażanie w chmurze

### Wymagania wstępne dla poniższych kroków

- Maszyna Linux (najlepiej Ubuntu) z zainstalowanymi Nano, Git i Docker

### Dodatkowe kroki

Przed uruchomieniem powyższych poleceń do pobrania repozytorium i instalacji:

1. Uruchom polecenia jako root, aby otworzyć niezbędne porty:
   - ufw enable
   - ufw allow 80 && ufw allow 443
   - ufw reload
   ---
   **OSTRZEŻENIE**

   ufw nie chroni portów opublikowanych przez Docker, ponieważ reguły iptables skonfigurowane przez Docker są analizowane przed tymi skonfigurowanymi przez ufw. Istnieje rozwiązanie zmieniające to zachowanie, ale wykracza poza zakres tego projektu. Upewnij się tylko, że cały ruch przechodzi przez usługę Caddy przez port 443. Port 80 powinien być używany tylko do przekierowania na port 443.

   ---
2. Uruchom skrypt **start-services.py** z argumentem środowiska **public**, aby wskazać, że zamierzasz uruchomić pakiet w publicznym środowisku. Skrypt upewni się, że wszystkie porty oprócz 80 i 443 są zamknięte, np.

```bash
   python3 start_services.py --profile gpu-nvidia --environment public
   ```

3. Skonfiguruj rekordy A u dostawcy DNS, aby skierować subdomeny ustawione w pliku .env dla Caddy
na adres IP instancji w chmurze.

   Na przykład, rekord A kierujący n8n na [IP instancji w chmurze] dla n8n.twojadomena.com


**UWAGA**: Jeśli używasz maszyny w chmurze bez domyślnie dostępnej komendy „docker compose", na przykład instancji GPU Ubuntu na DigitalOcean, uruchom te polecenia przed uruchomieniem start_services.py:

- DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\\\" -f4)
- sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
- sudo chmod +x /usr/local/bin/docker-compose
- sudo mkdir -p /usr/local/lib/docker/cli-plugins
- sudo ln -s /usr/local/bin/docker-compose /usr/local/lib/docker/cli-plugins/docker-compose

## Importowanie startowych workflow

Ten pakiet zawiera gotowe workflow n8n w folderze `n8n/backup/workflows/`. Aby je zaimportować:

1. Otwórz n8n pod adresem <http://localhost:5678/> (lub Twoją niestandardową domeną, jeśli wdrożone w chmurze)
2. Przejdź do listy workflow i kliknij menu z trzema kropkami lub użyj **Importuj z pliku**
3. Wybierz pliki JSON z folderu `n8n/backup/workflows/` na Twoim lokalnym komputerze

Szczegółowe instrukcje znajdziesz w [oficjalnej dokumentacji importu/eksportu n8n](https://docs.n8n.io/workflows/export-import/).

> [!NOTE]
> Po zaimportowaniu musisz utworzyć dane uwierzytelniające dla każdego workflow. Zobacz krok 3 w Szybkim starcie poniżej.

## ⚡️ Szybki start i użytkowanie

Głównym komponentem samodzielnie hostowanego starter kitu AI jest plik docker compose
wstępnie skonfigurowany z siecią i dyskiem, więc nie ma wiele więcej do
zainstalowania. Po wykonaniu powyższych kroków instalacji, postępuj zgodnie z poniższymi krokami,
aby rozpocząć.

1. Otwórz <http://localhost:5678/> w przeglądarce, aby skonfigurować n8n. Musisz
   to zrobić tylko raz. NIE tworzysz tutaj konta w n8n,
   to tylko lokalne konto dla Twojej instancji!
2. Zaimportuj workflow z `n8n/backup/workflows/` (zobacz [Importowanie startowych workflow](#importowanie-startowych-workflow)), a następnie otwórz go z listy workflow.
3. Utwórz dane uwierzytelniające dla każdej usługi:
   
   URL Ollama: http://ollama:11434

   Postgres (przez Supabase): użyj nazwy bazy danych, użytkownika i hasła z .env. WAŻNE: Host to 'db',
   ponieważ tak nazywa się usługa uruchamiająca Supabase

   URL Qdrant: http://qdrant:6333 (klucz API może być dowolny, ponieważ działa lokalnie)

   Google Drive: Postępuj zgodnie z [tym przewodnikiem od n8n](https://docs.n8n.io/integrations/builtin/credentials/google/).
   Nie używaj localhost jako URI przekierowania, po prostu użyj innej domeny, którą masz, i tak zadziała!
   Alternatywnie możesz skonfigurować [lokalne wyzwalacze plików](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.localfiletrigger/).
4. Wybierz **Testuj workflow**, aby rozpocząć uruchamianie workflow.
5. Jeśli uruchamiasz workflow po raz pierwszy, może być konieczne poczekanie,
   aż Ollama zakończy pobieranie Llama3.1. Możesz sprawdzić logi konsoli Docker,
   aby śledzić postęp.
6. Upewnij się, że przełączysz workflow jako aktywny i skopiujesz „Produkcyjny" URL webhooka!
7. Otwórz <http://localhost:3000/> w przeglądarce, aby skonfigurować Open WebUI.
Musisz to zrobić tylko raz. NIE tworzysz tutaj konta w Open WebUI,
to tylko lokalne konto dla Twojej instancji!
8. Przejdź do Workspace -> Funkcje -> Dodaj funkcję -> Nadaj nazwę + opis, a następnie wklej
kod z `n8n_pipe.py`

   Funkcja jest również [opublikowana na stronie Open WebUI](https://openwebui.com/f/coleam/n8n_pipe/).

9. Kliknij ikonę koła zębatego i ustaw n8n_url na produkcyjny URL webhooka,
który skopiowałeś w poprzednim kroku.
10. Włącz funkcję i teraz będzie dostępna w rozwijanym menu modeli w lewym górnym rogu!

Aby otworzyć n8n w dowolnym momencie, odwiedź <http://localhost:5678/> w przeglądarce.
Aby otworzyć Open WebUI w dowolnym momencie, odwiedź <http://localhost:3000/>.

Z Twoją instancją n8n będziesz mieć dostęp do ponad 400 integracji i
zestawu podstawowych i zaawansowanych węzłów AI, takich jak
[Agent AI](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.agent/),
[Klasyfikator tekstu](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.text-classifier/)
i [Ekstraktor informacji](https://docs.n8n.io/integrations/builtin/cluster-nodes/root-nodes/n8n-nodes-langchain.information-extractor/).
Aby zachować wszystko lokalnie, pamiętaj o użyciu węzła Ollama dla modelu
językowego i Qdrant jako magazynu wektorów.

> [!NOTE]
> Ten starter kit został zaprojektowany, aby pomóc Ci rozpocząć pracę z samodzielnie hostowanymi
> workflow AI. Chociaż nie jest w pełni zoptymalizowany pod środowiska produkcyjne,
> łączy solidne komponenty, które dobrze ze sobą współpracują w projektach proof-of-concept.
> Możesz go dostosować do swoich konkretnych potrzeb.

## Aktualizacja

Aby zaktualizować wszystkie kontenery do najnowszych wersji (n8n, Open WebUI itp.), uruchom te polecenia:

```bash
# Zatrzymaj wszystkie usługi
docker compose -p localai -f docker-compose.yml --profile <twoj-profil> down

# Pobierz najnowsze wersje wszystkich kontenerów
docker compose -p localai -f docker-compose.yml --profile <twoj-profil> pull

# Uruchom usługi ponownie z wybranym profilem
python start_services.py --profile <twoj-profil>
```

Zastąp `<twoj-profil>` jednym z: `cpu`, `gpu-nvidia`, `gpu-amd` lub `none`.

Uwaga: Sam skrypt `start_services.py` nie aktualizuje kontenerów — tylko je restartuje lub pobiera, jeśli pobierasz te kontenery po raz pierwszy. Aby uzyskać najnowsze wersje, musisz jawnie uruchomić powyższe polecenia.

## Rozwiązywanie problemów

Oto rozwiązania typowych problemów, które możesz napotkać:

### Problemy z Supabase

- **Supabase Pooler restartuje się**: Jeśli kontener supabase-pooler ciągle się restartuje, postępuj zgodnie z instrukcjami w [tym zgłoszeniu na GitHub](https://github.com/supabase/supabase/issues/30210#issuecomment-2456955578).

- **Awaria startu Supabase Analytics**: Jeśli kontener supabase-analytics nie uruchamia się po zmianie hasła Postgres, usuń folder `supabase/docker/volumes/db/data`.

- **Jeśli używasz Docker Desktop**: Wejdź w ustawienia Dockera i upewnij się, że opcja „Expose daemon on tcp://localhost:2375 without TLS" jest włączona

- **Supabase niedostępny** — Upewnij się, że nie masz znaku „@" w haśle Postgres! Jeśli połączenie z kontenerem kong działa (logi kontenera mówią, że odbiera żądania od n8n), ale n8n mówi, że nie może się połączyć, to zazwyczaj jest to problem, na podstawie tego, co udostępniła społeczność. Inne znaki mogą też być niedozwolone, symbol @ to jedyny, o którym wiem na pewno!

- **SearXNG restartuje się**: Jeśli kontener SearXNG ciągle się restartuje, uruchom polecenie „chmod 755 searxng" w folderze local-ai-packaged, aby SearXNG miał uprawnienia potrzebne do utworzenia pliku uwsgi.ini.

- **Brak plików w folderze Supabase** — Jeśli pojawią się błędy dotyczące brakujących plików w folderze supabase/ jak .env, docker/docker-compose.yml itp., najprawdopodobniej oznacza to, że miałeś „złe" pobranie repozytorium GitHub Supabase podczas uruchamiania skryptu start_services.py. Usuń folder supabase/ w folderze Local AI Package całkowicie i spróbuj ponownie.

### Problemy z obsługą GPU

- **Obsługa GPU w Windows**: Jeśli masz problemy z uruchomieniem Ollama z obsługą GPU w Windows z Docker Desktop:
  1. Otwórz ustawienia Docker Desktop
  2. Włącz backend WSL 2
  3. Zobacz [dokumentację Docker GPU](https://docs.docker.com/desktop/features/gpu/) po więcej szczegółów

- **Obsługa GPU w Linux**: Jeśli masz problemy z uruchomieniem Ollama z obsługą GPU na Linuxie, postępuj zgodnie z [instrukcjami Ollama Docker](https://github.com/ollama/ollama/blob/main/docs/docker.md).

### Problemy z węzłami n8n

- **Węzły Local File Trigger lub Execute Command niedostępne**: Począwszy od n8n v2+, te węzły są domyślnie wyłączone ze względów bezpieczeństwa. Aby je włączyć, odkomentuj `NODES_EXCLUDE=[]` w sekcji `x-n8n` pliku `docker-compose.yml` i zrestartuj n8n. Zobacz [Dostęp do lokalnych plików](#dostęp-do-lokalnych-plików) po szczegółowe instrukcje.

## 👓 Zalecana lektura

n8n jest pełen przydatnych treści do szybkiego rozpoczęcia pracy z koncepcjami AI
i węzłami. Jeśli napotkasz problem, przejdź do [wsparcia](#wsparcie).

- [Agenci AI dla deweloperów: od teorii do praktyki z n8n](https://blog.n8n.io/ai-agents/)
- [Samouczek: Zbuduj workflow AI w n8n](https://docs.n8n.io/advanced-ai/intro-tutorial/)
- [Koncepcje Langchain w n8n](https://docs.n8n.io/advanced-ai/langchain/langchain-n8n/)
- [Demonstracja kluczowych różnic między agentami a łańcuchami](https://docs.n8n.io/advanced-ai/examples/agent-chain-comparison/)
- [Czym są bazy wektorowe?](https://docs.n8n.io/advanced-ai/examples/understand-vector-databases/)

## 🎥 Przewodnik wideo

- [Przewodnik Cole'a po Local AI Starter Kit](https://youtu.be/pOsO40HSbOo)

## 🛍️ Więcej szablonów AI

Po więcej pomysłów na workflow AI odwiedź [**oficjalną galerię szablonów AI
n8n**](https://n8n.io/workflows/?categories=AI). Z każdego workflow
wybierz przycisk **Użyj workflow**, aby automatycznie zaimportować workflow do
Twojej lokalnej instancji n8n.

### Poznaj kluczowe koncepcje AI

- [Czat z agentem AI](https://n8n.io/workflows/1954-ai-agent-chat/)
- [Czat AI z dowolnym źródłem danych (używając również narzędzia workflow n8n)](https://n8n.io/workflows/2026-ai-chat-with-any-data-source-using-the-n8n-workflow-tool/)
- [Czat z asystentem OpenAI (z dodaniem pamięci)](https://n8n.io/workflows/2098-chat-with-openai-assistant-by-adding-a-memory/)
- [Użyj open-source'owego modelu LLM (przez HuggingFace)](https://n8n.io/workflows/1980-use-an-open-source-llm-via-huggingface/)
- [Czat z dokumentami PDF przy użyciu AI (z cytowaniem źródeł)](https://n8n.io/workflows/2165-chat-with-pdf-docs-using-ai-quoting-sources/)
- [Agent AI, który może scrapować strony internetowe](https://n8n.io/workflows/2006-ai-agent-that-can-scrape-webpages/)

### Lokalne szablony AI

- [Asystent ds. kodeksu podatkowego](https://n8n.io/workflows/2341-build-a-tax-code-assistant-with-qdrant-mistralai-and-openai/)
- [Rozbij dokumenty na notatki do nauki z MistralAI i Qdrant](https://n8n.io/workflows/2339-breakdown-documents-into-study-notes-using-templating-mistralai-and-qdrant/)
- [Asystent ds. dokumentów finansowych z Qdrant i](https://n8n.io/workflows/2335-build-a-financial-documents-assistant-using-qdrant-and-mistralai/) [ Mistral.ai](http://mistral.ai/)
- [Rekomendacje przepisów z Qdrant i Mistral](https://n8n.io/workflows/2333-recipe-recommendations-with-qdrant-and-mistral/)

## Porady i triki

### Dostęp do lokalnych plików

Samodzielnie hostowany starter kit AI utworzy współdzielony folder (domyślnie
zlokalizowany w tym samym katalogu), który jest zamontowany w kontenerze n8n i
pozwala n8n na dostęp do plików na dysku. Ten folder wewnątrz kontenera n8n znajduje się
pod ścieżką `/data/shared` — jest to ścieżka, której musisz użyć w węzłach, które
współpracują z lokalnym systemem plików.

**Węzły współpracujące z lokalnym systemem plików**

- [Odczyt/Zapis plików z dysku](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.filesreadwrite/)
- [Wyzwalacz lokalnych plików](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.localfiletrigger/)
- [Wykonaj polecenie](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.executecommand/)

**Włączanie węzłów Local File Trigger i Execute Command**

Począwszy od n8n v2+, węzły `Local File Trigger` i `Execute Command` są domyślnie wyłączone ze względów bezpieczeństwa. Aby je włączyć w tym lokalnym/samodzielnie hostowanym środowisku:

1. Otwórz `docker-compose.yml`
2. Znajdź sekcję `x-n8n` i odkomentuj linię `NODES_EXCLUDE`:
   ```yaml
   x-n8n: &service-n8n
     image: n8nio/n8n:latest
     environment:
       # ... inne zmienne ...
       - NODES_EXCLUDE=[]
   ```
3. Zrestartuj kontener n8n:
   ```bash
   docker compose -p localai -f docker-compose.yml --profile <twoj-profil> up -d n8n
   ```

Zobacz [Zmiany łamiące w n8n 2.0](https://docs.n8n.io/2-0-breaking-changes/#disable-executecommand-and-localfiletrigger-nodes-by-default) po więcej szczegółów.

## 📜 Licencja

Ten projekt (pierwotnie stworzony przez zespół n8n, link na górze README) jest objęty licencją Apache License 2.0 — szczegóły znajdziesz w pliku
[LICENSE](LICENSE).
