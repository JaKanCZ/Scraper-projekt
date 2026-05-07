"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Jakub Kankrlík
email: jakub@kankrlik.cz
discord: jakancz
"""

import sys
import csv
import requests
from bs4 import BeautifulSoup


BASE_URL = "https://www.volby.cz/pls/ps2017nss/"


def validate_arguments() -> tuple[str, str]:
    """
    Validate command-line arguments.
    Expected: python projekt_3.py <URL> <output_file.csv>
    Returns a tuple (url, output_file) if valid, otherwise exits.
    """
    if len(sys.argv) != 3:
        print(
            "CHYBA: Musíte zadat přesně 2 argumenty.\n"
            "Použití: python projekt_3.py <URL_územního_celku> <výstupní_soubor.csv>\n"
            "Příklad: python projekt_3.py "
            '"https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" '
            "vysledky_prostejov.csv"
        )
        sys.exit(1)

    url = sys.argv[1]
    output_file = sys.argv[2]

    if "volby.cz" not in url or "ps32" not in url:
        print(
            "CHYBA: Zadaný odkaz není platný odkaz na územní celek.\n"
            "Odkaz musí směřovat na stránku typu ps32 na volby.cz.\n"
            "Příklad: https://www.volby.cz/pls/ps2017nss/"
            "ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103"
        )
        sys.exit(1)

    if not output_file.endswith(".csv"):
        print("CHYBA: Výstupní soubor musí mít příponu .csv")
        sys.exit(1)

    return url, output_file


def get_page(url: str) -> BeautifulSoup:
    """
    Fetch a page and return a BeautifulSoup object.
    """
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def get_municipalities(district_url: str) -> list[dict]:
    """
    Parse the district page (ps32) and return a list of municipalities.
    Each municipality is a dict with keys: 'code', 'name', 'detail_url'.
    """
    soup = get_page(district_url)
    municipalities = []

    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue

            # First cell: municipality code (linked)
            code_link = cells[0].find("a")
            if not code_link:
                continue

            code = code_link.get_text(strip=True)
            # Skip non-numeric codes (e.g., header rows that slipped through)
            if not code.isdigit():
                continue

            name = cells[1].get_text(strip=True)
            href = code_link.get("href", "")
            detail_url = BASE_URL + href

            municipalities.append({
                "code": code,
                "name": name,
                "detail_url": detail_url,
            })

    return municipalities


def get_municipality_results(detail_url: str) -> dict:
    """
    Parse a municipality detail page (ps311) and return voting results.
    Returns a dict with keys:
        'registered', 'envelopes', 'valid' and party names as keys.
    """
    soup = get_page(detail_url)
    tables = soup.find_all("table")
    results = {}

    # --- Table 0: summary data ---
    if tables:
        summary_table = tables[0]
        summary_rows = summary_table.find_all("tr")
        # The data row is typically the last row (row index 2)
        for row in summary_rows:
            cells = row.find_all("td")
            if len(cells) >= 8:
                # cells layout (from inspection):
                # [0] Okrsky celkem, [1] zpr., [2] v %, [3] Voliči v seznamu,
                # [4] Vydané obálky, [5] Volební účast v %,
                # [6] Odevzdané obálky, [7] Platné hlasy, [8] % platných hlasů
                results["registered"] = cells[3].get_text(strip=True).replace("\xa0", "")
                results["envelopes"] = cells[4].get_text(strip=True).replace("\xa0", "")
                results["valid"] = cells[7].get_text(strip=True).replace("\xa0", "")
                break

    # --- Tables 1+ : party results ---
    for table in tables[1:]:
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) >= 3:
                # cells layout:
                # [0] Číslo strany, [1] Název strany, [2] Platné hlasy celkem,
                # [3] v %, [4] Předn. hlasy
                party_number = cells[0].get_text(strip=True)
                party_name = cells[1].get_text(strip=True)
                votes = cells[2].get_text(strip=True).replace("\xa0", "")
                # Skip rows where the party number is not numeric (artifacts)
                if party_number.isdigit() and party_name and votes:
                    results[party_name] = votes

    return results


def main():
    """Main function — orchestrates the scraping and CSV export."""
    url, output_file = validate_arguments()

    print(f"Stahuji data z: {url}")
    municipalities = get_municipalities(url)

    if not municipalities:
        print("CHYBA: Na zadané stránce nebyly nalezeny žádné obce.")
        sys.exit(1)

    print(f"Nalezeno {len(municipalities)} obcí. Stahuji výsledky hlasování...")

    # Collect all results; we need the first one to determine party columns
    all_results = []
    party_names = []

    for i, muni in enumerate(municipalities, start=1):
        results = get_municipality_results(muni["detail_url"])
        all_results.append(results)

        # Capture party column names from the first municipality
        if i == 1:
            party_names = [
                key for key in results
                if key not in ("registered", "envelopes", "valid")
            ]

        if i % 10 == 0 or i == len(municipalities):
            print(f"  Zpracováno {i}/{len(municipalities)} obcí...")

    # Build CSV header
    header = ["code", "name", "registered", "envelopes", "valid"] + party_names

    # Write to CSV
    with open(output_file, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(header)

        for muni, results in zip(municipalities, all_results):
            row = [
                muni["code"],
                muni["name"],
                results.get("registered", ""),
                results.get("envelopes", ""),
                results.get("valid", ""),
            ]
            for party in party_names:
                row.append(results.get(party, "0"))
            writer.writerow(row)

    print(f"HOTOVO! Výsledky uloženy do souboru: {output_file}")


if __name__ == "__main__":
    main()
