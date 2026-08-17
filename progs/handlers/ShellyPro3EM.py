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
        data[f"{prefix}voltage"] = str(em.get(f"{prefix}voltage"))
        data[f"{prefix}current"] = str(em.get(f"{prefix}current"))
        data[f"{prefix}freq"] = str(em.get(f"{prefix}freq"))    
        data[f"{prefix}act_power"] = str(em.get(f"{prefix}act_power"))
        data[f"{prefix}aprt_power_va"] = str(em.get(f"{prefix}aprt_power"))
        data[f"{prefix}pf"] = str(em.get(f"{prefix}pf"))
        data[f"{prefix}total_act_energy_wh"] = str(emdata.get(f"{prefix}total_act_energy"))
        data[f"{prefix}total_act_ret_energy_wh"] = str(emdata.get(f"{prefix}total_act_ret_energy"))
        phases_dict[phase_name] = {
            "voltage_v": em.get(f"{prefix}voltage"),
            "current_a": em.get(f"{prefix}current"),
            "freq_hz": em.get(f"{prefix}freq"),
            "act_power_w": em.get(f"{prefix}act_power"),
            # Korrigiert: aprt_power statt apower 🟢
            "aprt_power_va": em.get(f"{prefix}aprt_power"),
            "pf": em.get(f"{prefix}pf"),
            # Korrigiert: Direktes Auslesen der Phasen-Energiewerte aus emdata:0
            "total_act_energy_wh": emdata.get(f"{prefix}total_act_energy"),
            "total_act_ret_energy_wh": emdata.get(
                f"{prefix}total_act_ret_energy"
            ),
        }

    data['mac'] = status_data.get("sys", {}).get("mac")
    data['uptime_seconds'] = status_data.get("sys", {}).get("uptime")
    data['temperature_c'] = status_data.get("temperature:0", {}).get("tC")  # Korrigiert: Liegt in 'temperature:0' 🟢
    data['total_current_a'] = em.get("total_current")
    data['total_act_power_w'] = em.get("total_act_power")
    data['total_aprt_power_va'] = em.get("total_aprt_power")  # Korrigiert: aprt_power statt apower 🟢
    data['total_act_energy_wh'] = emdata.get("total_act")  # Korrigiert: Keys heißen laut deinem JSON total_act und total_act_ret  🟢
    data['total_act_ret_energy_wh'] = emdata.get("total_act_ret")  # Korrigiert: Keys heißen laut deinem JSON total_act und total_act_ret  🟢
    
    result = {
        "device_info": {
            "mac": status_data.get("sys", {}).get("mac"),
            "uptime_seconds": status_data.get("sys", {}).get("uptime"),
            "temperature_c": status_data.get("temperature:0", {}).get(
                "tC"
            ),  # Korrigiert: Liegt in 'temperature:0' 🟢
        },
        "total_current_metrics": {
            "total_current_a": em.get("total_current"),
            "total_act_power_w": em.get("total_act_power"),
            # Korrigiert: aprt_power statt apower 🟢
            "total_aprt_power_va": em.get("total_aprt_power"),
        },
        "total_energy_counters": {
            # Korrigiert: Keys heißen laut deinem JSON total_act und total_act_ret 🟢
            "total_act_energy_wh": emdata.get("total_act"),
            "total_act_ret_energy_wh": emdata.get("total_act_ret"),
        },
        "phases": phases_dict,
    }

    return data
