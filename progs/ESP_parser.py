import requests
import re
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)

def parse_ESP(text):    
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
