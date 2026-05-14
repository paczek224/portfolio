# Portfolio Multi-Agent Starter

Minimalny projekt startowy do generowania prostej strony portfolio na podstawie CV.

## Co zawiera

- `orchestrator/` - Pythonowy system multi-agentowy:
  - `OrchestratorAgent` koordynuje pracę.
  - `BackendAgent` przygotowuje dane dla Spring Boot.
  - `FrontendAgent` przygotowuje dane i instrukcje dla Reacta.
- `backend/` - bardzo prosty backend Java Spring Boot.
- `frontend/` - bardzo prosty frontend React + Vite.
- `generated/` - katalog na pliki wygenerowane z CV.

Całość używa darmowych bibliotek i jest przygotowana tak, aby model LLM można było wymienić przez konfigurację.

## Wymagania

- Python 3.11+
- Java 17+
- Node.js 20+
- Lokalny model dostępny przez Ollama albo serwer kompatybilny z OpenAI API.

Przykład dla Ollama:

```powershell
ollama serve
ollama pull qwen3.6
```

Jeśli Twoja nazwa modelu w Ollama jest inna, ustaw ją w `.env`.

## Start

1. Skopiuj konfigurację:

```powershell
Copy-Item .env.example .env
```

2. Zainstaluj zależności orkiestratora:

```powershell
cd orchestrator
python -m pip install -e .
```

3. Wklej swoje CV jako tekst albo wrzuć PDF do katalogu `input`, na przykład:

```powershell
New-Item -ItemType Directory -Force input
notepad input\cv.txt
```

albo:

```powershell
Copy-Item C:\sciezka\do\twojego-cv.pdf input\cv.pdf
```

4. Uruchom orkiestrator jednorazowo:

```powershell
cd orchestrator
python run.py --cv ..\input\cv.txt
```

PDF uruchomisz tak:

```powershell
python run.py --cv ..\input\cv.pdf
```

Mozesz tez uruchomic tryb interaktywny:

```powershell
python run.py chat
```

Przykladowe polecenia w chacie:

```text
generuj portfolio z ../input/cv.pdf
przetworz ../input/cv.txt
pokaz dane
model
pomoc
wyjdz
```

5. Uruchom backend:

```powershell
cd ..\backend
mvn spring-boot:run
```

6. Uruchom frontend:

```powershell
cd ..\frontend
npm install
npm run dev
```

Frontend domyślnie oczekuje backendu pod `http://localhost:8080`.

## Docker

Backend i frontend mozna uruchomic razem przez Docker Compose:

```powershell
docker compose up --build
```

Po starcie:

- frontend: `http://localhost:8081`
- backend API: `http://localhost:8080/api/portfolio`

Frontend w kontenerze jest serwowany przez Nginx. Zapytania do `/api` sa proxy'owane do kontenera `backend`, wiec w Dockerze nie trzeba ustawiac adresu API w przegladarce.

## Zmiana modelu

Najprościej zmienić wartości w `.env`:

```env
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=qwen3.6
```

Dla serwera kompatybilnego z OpenAI API:

```env
LLM_PROVIDER=openai_compatible
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL=twoj-model
LLM_API_KEY=opcjonalny-klucz
```

## Uwagi

To jest celowo prosty start. Orkiestrator potrafi użyć LLM do ekstrakcji danych z CV, ale ma też fallback heurystyczny, żeby projekt nie blokował się, jeśli model lokalny jeszcze nie działa.
