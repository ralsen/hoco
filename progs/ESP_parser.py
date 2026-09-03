import requests
import re
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

ESP_Trans = {
    'Hostname': 'name',
    'IP': 'IP',
    'Type': 'Type',
    'Version': 'Version',
    'Hardw': 'Hardware',
    'Network': 'Network',
    'Chip-ID': None,  
    'MAC-Address': 'MAC',
    'Network-IP': 'IP',
    'Devicename': 'hostname',
    'AP-Name': 'APName',
    'cfg-Size': 'Size',
    'Hash': 'Hash',
    'Display': None,
    'uptime': 'uptime',
    'Measuring cycle': 'MeasuringCycle',
    'Transmit cycle': 'TransmitCycle',
    'PageReload cycle': 'PageReload',
    'Signal strength': 'WiFi',
    'Server': 'Server',
    'Port': 'Port',
    'LED': 'LED',
    'Measurements': None,
    'good Transmissions': 'goodTrans',
    'bad Transmissions': 'badTrans',
    'Pages delivered': 'delivPages'
    }
     
Switch_Trans = {
    'ontime': 'ontime',
    'offtime': 'offtime',
    'Cycles': 'cycles',
    }
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
            keysplit = key.split(">")[-1]
            keytrans = ESP_Trans.get(keysplit, 'NoTranslation')
            if keytrans == 'NoTranslation':
                keytrans = Switch_Trans.get(keysplit, 'NoTranslation')
            logger.debug(f"Parsing key: {key}, Translation: {keytrans}")
            if keytrans == 'NoTranslation':
                logger.warning(f"Key '{keysplit}' has no translation and will be ignored.")
            elif keytrans is not None:
                data_dict[keytrans] = value.strip()
                
    try:
        data_dict["hostname"]
    except KeyError:
        data_dict["hostname"] = "ESP_Device ohne Hostname"
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
        return value

def parse_ESP_tof(html: str) -> str:
    match = re.search(r'<h1[^>]*font-size:128px[^>]*>(\d+)</h1>', html)

    if match:
        value = int(match.group(1))
        return value

