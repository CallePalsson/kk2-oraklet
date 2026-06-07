# KK2 Oraklet

Detta projekt är byggt som en del av KK2 och har som syfte att kombinera
dataanalys med en mindre språkmodell.

Applikationen är ett REST API byggt med FastAPI där användaren kan ladda upp
en CSV fil, hämta statistik från datan och ställa frågor om datasetet.
Pandas används för att läsa och analysera filen och SmolLM2 används för att
generera ett svar.

AI flödet är uppdelat i en egen typad Runnable kedja:

```python
PromptBuilder() | LLMRunner() | ResponseParser()
```

Varje steg har ett eget ansvar. PromptBuilder bygger prompten från frågan och
statistiken, LLMRunner skickar prompten till modellen och ResponseParser tar
hand om modellens svar.

## Tekniker

Projektet använder:

- Python
- FastAPI
- Pandas
- Pydantic
- Transformers
- SmolLM2
- Pytest
- uv

## Installation

Klona repot och gå in i projektmappen.

Installera sedan projektets dependencies:

```bash
uv sync
```

Modellen laddas ner första gången `/ai/ask` används. Standardmodellen är:

```text
HuggingFaceTB/SmolLM2-135M-Instruct
```

Det går att ändra modell och maxstorlek på uppladdade filer med en `.env` fil:

```env
MODEL_NAME=HuggingFaceTB/SmolLM2-135M-Instruct
MAX_UPLOAD_BYTES=1000000
```

`.env` är exkluderad från Git genom `.gitignore`.

## Starta applikationen

Starta servern med:

```bash
uv run uvicorn app.main:app --reload
```

Swagger dokumentationen finns sedan på:

```text
http://127.0.0.1:8000/docs
```

## Endpoints

### Health check

```http
GET /health
```

Returnerar:

```json
{
  "status": "ok"
}
```

### Ladda upp CSV

```http
POST /data/upload
```

Endpointen tar emot en CSV fil som form-data. Datasetet sparas tillfälligt i
minnet och försvinner när servern startas om.

Exempel:

```bash
curl -X POST "http://127.0.0.1:8000/data/upload" \
  -F "file=@water.csv"
```

Svaret innehåller antal rader, kolumner och datatyper:

```json
{
  "rows": 2,
  "columns": ["place", "water_temp_c"],
  "dtypes": {
    "place": "object",
    "water_temp_c": "float64"
  }
}
```

### Hämta statistik

```http
GET /data/stats
```

Returnerar statistik skapad med Pandas `describe()`. Om inget dataset har
laddats upp returneras ett 404 fel.

```bash
curl "http://127.0.0.1:8000/data/stats"
```

### Ställ en fråga

```http
POST /ai/ask
```

Endpointen skickar statistik och användarens fråga genom Runnable kedjan.
Ett dataset måste vara uppladdat innan det går att ställa en fråga.

```bash
curl -X POST "http://127.0.0.1:8000/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"Vilken badplats har varmast vatten?"}'
```

Exempel på svar:

```json
{
  "question": "Vilken badplats har varmast vatten?",
  "answer": "Bryggan har högst vattentemperatur.",
  "model": "HuggingFaceTB/SmolLM2-135M-Instruct"
}
```

Eftersom svaret genereras av en språkmodell kan innehållet variera och modellen
kan ibland ge ett felaktigt svar.

## Testa endpoints med Postman

Jag använder Postman för att testa applikationens endpoints. Servern behöver
vara startad innan requests kan skickas:

```bash
uv run uvicorn app.main:app --reload
```

Adressen som används i Postman är:

```text
http://127.0.0.1:8000
```

För att ladda upp ett dataset skapar jag en `POST` request till
`/data/upload`. Under Body väljer jag `form-data`, skriver `file` som key och
ändrar typen från Text till File. Sedan väljer jag den CSV fil som ska laddas
upp.

Efter uppladdningen går det att skicka en `GET` request till `/data/stats` för
att se statistik om datasetet.

För att ställa en fråga skapar jag en `POST` request till `/ai/ask`. Under
Body väljer jag raw och JSON och skickar exempelvis:

```json
{
  "question": "Vilken badplats har varmast vatten?"
}
```

Jag använder även `GET /health` för att kontrollera att servern är igång.

## Tester

Testerna körs med:

```bash
uv run pytest app/tests/ -v
```

Tester finns för endpoints, prompt builder, response parser, Runnable kedjan
och fel från modellen. Modellen är mockad i testerna för att de ska gå snabbt
och inte behöva ladda SmolLM2 varje gång.

## Projektstruktur

```text
app/
├── chain/
│   ├── pipeline.py
│   ├── runnable.py
│   └── steps.py
├── tests/
│   ├── test_chain.py
│   └── test_endpoints.py
├── config.py
├── data.py
├── main.py
└── schemas.py
```

En begränsning i projektet är att bara ett dataset sparas i minnet åt gången.
Detta fungerar för uppgiften men hade behövt byggas om med exempelvis en
databas eller separat fillagring om applikationen skulle användas av flera
användare.

Modellen får bara statistik från Pandas `describe()` och inte hela datasetet.
Därför fungerar den bäst för enklare frågor om till exempel medelvärde, min och
max. Eftersom SmolLM2 är en liten lokal modell kan svaren också bli enklare
eller ibland felaktiga jämfört med större AI modeller.
