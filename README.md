# Scraper výsledků voleb do Poslanecké sněmovny 2017

## Popis projektu

Tento projekt obsahuje Python skript, který scrapuje výsledky hlasování
z voleb do Poslanecké sněmovny Parlamentu České republiky konaných
ve dnech 20.–21. října 2017.

Skript stáhne data pro zvolený územní celek (okres) a uloží je do
souboru CSV. Pro každou obec jsou uloženy:
- kód a název obce
- počet voličů v seznamu, vydaných obálek a platných hlasů
- počet hlasů pro každou kandidující stranu

## Instalace

1. Naklonujte si repozitář a přejděte do složky projektu:
   ```
   git clone <URL_repozitáře>
   cd <název_složky>
   ```

2. Vytvořte a aktivujte virtuální prostředí:
   ```
   python -m venv venv

   # Windows:
   venv\Scripts\activate

   # macOS / Linux:
   source venv/bin/activate
   ```

3. Nainstalujte potřebné knihovny:
   ```
   pip install -r requirements.txt
   ```

## Spuštění

Skript vyžaduje přesně **dva argumenty** příkazové řádky:
1. **URL** – odkaz na územní celek (stránka `ps32` na webu volby.cz)
2. **Výstupní soubor** – jméno CSV souboru, kam se data uloží

```
python projekt_3.py "<URL_územního_celku>" <výstupní_soubor.csv>
```

## Ukázka použití

Stáhnutí výsledků pro okres **Prostějov**:

```
python projekt_3.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" vysledky_prostejov.csv
```

Výstup programu:
```
Stahuji data z: https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103
Nalezeno 97 obcí. Stahuji výsledky hlasování...
  Zpracováno 10/97 obcí...
  ...
  Zpracováno 97/97 obcí...
HOTOVO! Výsledky uloženy do souboru: vysledky_prostejov.csv
```

Ukázka prvních řádků výstupního souboru `vysledky_prostejov.csv`:

| code | name | registered | envelopes | valid | Občanská demokratická strana | ... | Svob.a př.dem.-T.Okamura (SPD) |
|------|------|-----------|-----------|-------|------------------------------|-----|-------------------------------|
| 506761 | Alojzov | 205 | 145 | 144 | 29 | ... | 15 |
| 589268 | Bedihošť | 834 | 527 | 524 | 51 | ... | 82 |
