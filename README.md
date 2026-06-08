# KK2 Oraklet

Syftet med detta projekt var att bygga ett REST API som kombinerar
dataanalys med en mindre språkmodell. Användaren kan ladda upp en CSV fil,
se statistik om datasetet och sedan ställa frågor om datan.

Applikationen är byggd med FastAPI och Pandas används för att läsa och
analysera CSV filen. AI delen använder den lokala modellen SmolLM2 via
Transformers. Eftersom modellen körs lokalt behövs ingen API nyckel och datan
skickas inte vidare till en extern AI tjänst.

## Applikationens struktur och flöde

Projektet är uppdelat så att varje del har ett tydligt ansvar. `main.py`
innehåller alla endpoints, `data.py` hanterar datasetet och `schemas.py`
innehåller Pydantic modellerna som används för input och output.

AI flödet ligger i `chain/` och är uppdelat i tre steg:

```python
PromptBuilder() | LLMRunner() | ResponseParser()
```

`PromptBuilder` bygger en prompt från användarens fråga och statistiken från
Pandas. `LLMRunner` skickar prompten till SmolLM2 och `ResponseParser` tar hand
om modellens råa svar. Jag valde denna struktur eftersom det blir enklare att
förstå och testa varje del separat istället för att lägga all logik i en stor
funktion.

Flödet fungerar ungefär så här:

1. Användaren laddar upp en CSV fil
2. Pandas läser filen och sparar datasetet i minnet
3. Statistik skapas med `describe()`
4. Användaren skickar en fråga till `/ai/ask`
5. Frågan och statistiken skickas genom Runnable kedjan
6. Modellen genererar ett svar som returneras som JSON

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

## Installation och start

Klona repot och gå in i projektmappen. Installera sedan projektets
dependencies:

```bash
uv sync
```

Starta applikationen med:

```bash
uv run uvicorn app.main:app --reload
```

Servern körs sedan på:

```text
http://127.0.0.1:8000
```

Swagger dokumentationen finns på:

```text
http://127.0.0.1:8000/docs
```

SmolLM2 laddas ner första gången `/ai/ask` används. Standardmodellen är:

```text
HuggingFaceTB/SmolLM2-135M-Instruct
```

Det går även att ändra modell eller maxstorleken för uppladdade filer i en
`.env` fil:

```env
MODEL_NAME=HuggingFaceTB/SmolLM2-135M-Instruct
MAX_UPLOAD_BYTES=1000000
```

`.env` finns med i `.gitignore` och ska inte checkas in i Git.

## Endpoints

### GET /health

Används för att kontrollera att servern är igång.

```json
{
  "status": "ok"
}
```

### POST /data/upload

Tar emot en CSV fil som form-data. Datasetet sparas tillfälligt i minnet och
försvinner när servern startas om.

```bash
curl -X POST "http://127.0.0.1:8000/data/upload" \
  -F "file=@water.csv"
```

Exempel på svar:

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

### GET /data/stats

Returnerar statistik från Pandas `describe()`. Ett dataset måste vara
uppladdat först, annars returneras ett 404 fel.

```bash
curl "http://127.0.0.1:8000/data/stats"
```

### POST /ai/ask

Tar emot en fråga om datasetet och skickar den genom Runnable kedjan. Ett
dataset måste vara uppladdat innan det går att ställa en fråga.

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

## Testa med Postman

Jag använder främst Postman för att testa applikationens endpoints. Servern
behöver vara startad innan requests kan skickas.

För att ladda upp en CSV fil skapar jag en `POST` request till
`http://127.0.0.1:8000/data/upload`. Under Body väljer jag `form-data`, skriver
`file` som key och ändrar typen från Text till File. Sedan väljer jag filen som
ska laddas upp.

Efter uppladdningen går det att skicka en `GET` request till `/data/stats`.

För att ställa en fråga skapar jag en `POST` request till `/ai/ask`. Under Body
väljer jag raw och JSON och skickar exempelvis:

```json
{
  "question": "Vilken badplats har varmast vatten?"
}
```

## Tester

Testerna körs med:

```bash
uv run pytest app/tests/ -v
```

Det finns tester för API endpoints, PromptBuilder, ResponseParser och hela
Runnable kedjan. Modellen mockas i testerna eftersom det gör testerna snabbare
och mer stabila. Det finns även tester för saknat dataset och fel när modellen
inte går att ladda.

## Begränsningar och förbättringar

En begränsning är att bara ett dataset sparas i minnet åt gången. Detta
fungerar bra för projektets storlek men hade behövt byggas om med exempelvis en
databas om flera användare skulle använda applikationen samtidigt.

Modellen får bara statistik från Pandas `describe()` och inte hela datasetet.
Det betyder att den fungerar bäst för enklare frågor om till exempel
medelvärde, min och max. SmolLM2 är även en ganska liten modell och kan ibland
ge enklare eller felaktiga svar jämfört med större AI modeller.

Hade jag byggt vidare på projektet hade jag velat förbättra analysen av
datasetet, lägga till mer loggning och göra det möjligt att hantera flera
dataset samtidigt.
