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
"""
{
    "ble":{},
    "bthome":{"errors":["bluetooth_disabled"]},
    "cloud":{"connected":true},
    "em:0":{"id":0,"a_current":0.028,"a_voltage":0.0,"a_act_power":0.0,"a_aprt_power":0.0,"a_pf":0.00,"a_freq":0.0,"b_current":0.027,"b_voltage":0.0,"b_act_power":0.0,"b_aprt_power":0.0,"b_pf":0.00,"b_freq":0.0,"c_current":1.137,"c_voltage":233.1,"c_act_power":142.6,"c_aprt_power":265.0,"c_pf":0.54,"c_freq":50.0,"n_current":null,"total_current":1.192,"total_act_power":142.605,"total_aprt_power":264.956, "user_calibrated_phase":[]},
    "emdata:0":{"id":0,"a_total_act_energy":0.03,"a_total_act_ret_energy":0.00,"b_total_act_energy":0.03,"b_total_act_ret_energy":0.00,"c_total_act_energy":95884.06,"c_total_act_ret_energy":5123.04,"total_act":95884.11, "total_act_ret":5123.04},
    "eth":{"ip":null,"ip6":null
    "modbus":{},
    "mqtt":{"connected":false},
    "sys":{"mac":"ECE334F6A15C","restart_required":false,"time":"14:01","unixtime":1782475286,"last_sync_ts":1782473602,"uptime":1540733,"ram_size":244376,"ram_free":103304,"ram_min_free":81808,"fs_size":524288,"fs_free":192512,"cfg_rev":12,"kvs_rev":0,"schedule_rev":0,"webhook_rev":0,"btrelay_rev":0,"available_updates":{"beta":{"version":"2.0.0-beta2"}},
           "reset_reason":3,"utc_offset":7200},
    "temperature:0":{"id": 0,"tC":45.5, "tF":113.9},
    "wifi":{"sta_ip":"192.168.2.123","status":"got ip","ssid":"janzneu","bssid":"08:b6:57:c5:84:96","rssi":-63,"sta_ip6":["fe80::eee3:34ff:fef6:a15c","2a02:3100:8792:aa00:eee3:34ff:fef6:a15c","fd37:996c:b6d2:0:eee3:34ff:fef6:a15c"]},
    "ws":{"connected":false}
}
"""
{'online': True, 'device_info': {'mac': 'ECE334F6A15C', 'uptime_seconds': 1541022, 'temperature_c': None}, 'total_current_metrics': {'total_act_power_w': 209.98, 'total_apower_va': None, 'total_rpower_var': None}, 'total_energy_counters': {'total_act_energy_wh': None, 'total_act_ret_energy_wh': None}, 'phases': {'A': {...}, 'B': {...}, 'C': {...}}, 'saldated_metrics': {'current_saldated_power_w': 210.0, 'total_saldated_energy_wh': 0}, 'raw_status': {'ble': {}, 'bthome': {...}, 'cloud': {...}, 'em:0': {...}, 'emdata:0': {...}, 'eth': {...}, 'modbus': {}, 'mqtt': {...}, 'sys': {...}, 'temperature:0': {...}, 'wifi': {...}, 'ws': {...}}}