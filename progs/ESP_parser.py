import requests
import re
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

def parse_ESP_main(text):    
    # Extrahiere nur den Inhalt zwischen <div1> und </div1>
    div1_content = re.search(r'<div1>(.*?)</div1>', text, re.DOTALL).group(1)

    # Extrahiere alle Schlüssel-Wert-Paare, ignoriere leere Zeilen und <br>-Tags
    matches2 = re.findall(r'([^:<]+):\s*([^<]+)', div1_content)
    data = {key: value for key, value in matches2}

    data_dict = {}
    for key, value in data.items():
        if key.startswith("/h3>\r\n-----> "):
            cleaned_key = key.split("V", 1)[-1]
            version = cleaned_key.split(" ", 1)[0]
            data_dict["Version"] = f"V{version}"
        else:
            data_dict[key.split(">")[-1]] = value.strip()

    try:
        data_dict["Hostname"]
    except KeyError:
        data_dict["Hostname"] = "ESP_Device ohne Hostname"
    return data_dict

def parse_ESP_table(html: str) -> list[dict]:
    """
    Extrahiert Tabellenwerte ohne BeautifulSoup.
    Erwartet eine Tabelle mit:
    - Header in erster Zeile
    - Danach <tr><td>channel</td><td>Temperatur</td></tr>
    """

    result = []

    # Tabelle isolieren
    table_start = html.find("<table")
    table_end = html.find("</table>")

    if table_start == -1 or table_end == -1:
        return result  # sollte laut Vorgabe nicht passieren

    table_html = html[table_start:table_end]

    # Alle Zeilen holen
    rows = table_html.split("<tr>")

    # Erste Zeile ist Header → überspringen
    for row in rows[2:]:
        cols = row.split("<td>")

        if len(cols) >= 3:
            # Inhalt extrahieren (bis </td>)
            channel = cols[1].split("</td>")[0].strip()
            temp = cols[2].split("</td>")[0].strip()

            result.append({
                "channel": channel,
                "Temperatur": temp
            })
    return result

def parse_ESP_switch(html: str) -> list[dict]:
    match = re.search(r'Schalter ist:\s*([^<]+)', html, re.IGNORECASE)
    if match:
        value = match.group(1)
        print(value)    
        return value

def parse_ESP_tof(html: str) -> str:
    match = re.search(r'<h1[^>]*font-size:128px[^>]*>(\d+)</h1>', html)

    if match:
        value = int(match.group(1))
        print(value)    
        return value

