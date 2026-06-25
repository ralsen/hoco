from dispatcher import Dispatcher
import logging
import json

logger = logging.getLogger(__name__)
logging.getLogger('urllib3').setLevel(logging.WARNING)

@Dispatcher.register("S3PM-001PCEU16")
def handle_Pro3EM(self):
    logger.debug("Handling: S3PM-001PCEU16")
    data = {}
    data['name'] = self.this['device']['Hostname']
    data['Type'] = self.this['device']['Type']
    data['IP'] = self.this['device']['IP']
    status_data = json.loads(self.this['response'].text)
    # Die beiden Haupt-Datenblöcke für die Energiemessung
    em = status_data.get("em:0", {})
    emdata = status_data.get("emdata:0", {})

    # Dynamische Zuordnung der Phasen-Präfixe in der Shelly-API
    # Shelly nutzt z.B. 'a_voltage' für Phase A, 'b_voltage' für Phase B, etc.
    phases_keys = {"A": "a_", "B": "b_", "C": "c_"}
    phases_dict = {}

    for phase_name, prefix in phases_keys.items():
        phases_dict[phase_name] = {
            # --- Echtzeit-Messwerte (aus em:0) ---
            "voltage_v": em.get(f"{prefix}voltage"),  # Spannung (V)
            "current_a": em.get(f"{prefix}current"),  # Stromstärke (A)
            "act_power_w": em.get(
                f"{prefix}act_power"
            ),  # Wirkleistung (W) - negativ bei Einspeisung
            "apower_va": em.get(
                f"{prefix}apower"
            ),  # Scheinleistung (VA) 🟢
            "rpower_var": em.get(
                f"{prefix}rpower"
            ),  # Blindleistung (var) 🟢
            "pf": em.get(f"{prefix}pf"),  # Leistungsfaktor (Power Factor)
            # --- Kumulierte Energiezähler (aus emdata:0) ---
            "total_act_energy_wh": emdata.get(
                f"{prefix}total_act_energy"
            ),  # Bezogene Wirkenergie (Wh)
            "total_act_ret_energy_wh": emdata.get(
                f"{prefix}total_act_ret_energy"
            ),  # Eingespeiste Wirkenergie (Wh) 🟢
            "total_react_energy_varh": emdata.get(
                f"{prefix}total_react_energy"
            ),  # Bezogene Blindarbeit (varh)
            "total_react_ret_energy_varh": emdata.get(
                f"{prefix}total_react_ret_energy"
            ),  # Eingespeiste Blindarbeit (varh)
        }

    # Zusammenfassung des Gesamtsystems (Total-Werte)
    result = {
        "online": True,
        "device_info": {
            "mac": status_data.get("sys", {}).get("mac"),
            "uptime_seconds": status_data.get("sys", {}).get("uptime"),
            "temperature_c": status_data.get("sys", {}).get(
                "temperature", {}
            ).get("tC"),
        },
        # --- Gesamtes System aktuell ---
        "total_current_metrics": {
            "total_act_power_w": em.get(
                "total_act_power"
            ),  # Gesamte Wirkleistung (W)
            "total_apower_va": em.get(
                "total_apower"
            ),  # Gesamte Scheinleistung (VA) 🟢
            "total_rpower_var": em.get(
                "total_rpower"
            ),  # Gesamte Blindleistung (var) 🟢
        },
        # --- Gesamtes System kumuliert ---
        "total_energy_counters": {
            "total_act_energy_wh": emdata.get(
                "total_act_energy"
            ),  # Gesamter Bezug (Wh)
            "total_act_ret_energy_wh": emdata.get(
                "total_act_ret_energy"
            ),  # Gesamte Einspeisung (Wh) 🟢
        },
        # Die drei einzelnen Phasen
        "phases": phases_dict,
        # Mathematisch saldierte Werte (wichtig für D/AT/CH Stromzähler)
        "saldated_metrics": {
            "current_saldated_power_w": sum(
                em.get(f"{p}act_power", 0) for p in ["a_", "b_", "c_"]
            ),
            "total_saldated_energy_wh": emdata.get("total_act_energy", 0)
            - emdata.get("total_act_ret_energy", 0),
        },
        # Falls man doch mal ein verstecktes JSON-Feld sucht:
        "raw_status": status_data,
    }

    return result

