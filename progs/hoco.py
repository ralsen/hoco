#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###############################################################
import time
import logging 
import os
import json
import requests

import config as config
import hocohandler as dh
from registry import registry
from dispatcher import Dispatcher, load_handlers

logger = logging.getLogger(__name__)

text = '{"device":{"type":"SHPLG2-1","mac":"083A8DF437C7","hostname":"shellyplug-083A8DF437C7","num_outputs":1,"num_meters":1},"wifi_ap":{"enabled":false,"ssid":"shellyplug-083A8DF437C7","key":""},"wifi_sta":{"enabled":true,"ssid":"janzneu","ipv4_method":"dhcp","ip":null,"gw":null,"mask":null,"dns":null},"wifi_sta1":{"enabled":false,"ssid":null,"ipv4_method":"dhcp","ip":null,"gw":null,"mask":null,"dns":null},"ap_roaming":{"enabled":false,"threshold":-70},"mqtt": {"enable":false,"server":"192.168.33.3:1883","user":"","id":"shellyplug-083A8DF437C7","reconnect_timeout_max":60.000000,"reconnect_timeout_min":2.000000,"clean_session":true,"keep_alive":60,"max_qos":0,"retain":false,"update_period":30},"coiot": {"enabled":true,"update_period":15,"peer":""},"sntp":{"server":"time.google.com","enabled":true},"login":{"enabled":false,"unprotected":false,"username":"admin"},"pin_code":"","name":null,"fw":"20230913-113610/v1.14.0-gcb84623","pon_wifi_reset":false,"discoverable":false,"build_info":{"build_id":"20230913-113610/v1.14.0-gcb84623","build_timestamp":"2023-09-13T11:36:10Z","build_version":"1.0"},"cloud":{"enabled":true,"connected":true},"timezone":"Europe/Berlin","lat":52.477100,"lng":9.531200,"tzautodetect":true,"tz_utc_offset":3600,"tz_dst":false,"tz_dst_auto":true,"time":"15:17","unixtime":1742393834,"led_status_disable":false,"debug_enable":false,"allow_cross_origin":false,"actions":{"active":false,"names":["btn_on_url","out_on_url","out_off_url"]},"hwinfo":{"hw_revision":"prod-191018","batch_id":1},"max_power":3500,"relays":[{"name":null,"appliance_type":"General","ison":true,"has_timer":false,"default_state":"on","auto_on":5.00,"auto_off":0.00,"schedule":false,"schedule_rules":[],"max_power":3500}],"eco_mode_enabled":true}'

data = json.loads(text)

def get_all_shelly_pro_3em_data(ip_address):
    """Holt absolut alle Messwerte eines Shelly Pro 3EM und strukturiert sie in einem Dictionary."""
    url = f"http://{ip_address}/rpc/Shelly.GetStatus"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        status_data = response.json()

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

    except requests.exceptions.RequestException as e:
        return {"online": False, "error": str(e)}

if __name__ == "__main__":
    current_file_path = os.path.realpath(__file__)
    current_file_name = os.path.basename(current_file_path)

    cfg = config.InitManager(current_file_name).ini

    logger.info("")
    logger.info(f'---------- Starte {current_file_path} ----------') 

    load_handlers()

    logger.debug("Searching Devices ...")
    devhandler = dh.DeviceHandler(cfg)
    devices = devhandler.discover_devices()
    reg = registry(cfg)
    
    # ganz wichtig: einmal aufrufen
    #data = {"Type": "SNSW-001X16EU"}
    #d = Dispatcher(data)
    #cfg['dispatchers'] = d
    #logger.debug(f"Handling device: {d.handle()}")

    old_x = []
    i = 0
    data = get_all_shelly_pro_3em_data("192.168.2.13")
    try:
        while True:
            logger.info(f"Mainloop iteration: {i}")
            i += 1
            x = cfg['ThreadManager'].get_all()
            if x == old_x:
                logger.info(f"{len(x)} active threads. No changes.")
            else:
                new_threads = set(x) - set(old_x)   # neu dazugekommen
                mis_threads = set(old_x) - set(x)    # weggefallen
                logger.info(f"{len(x)} active Threads:")
                logger.info(f"New thread(s):     {new_threads}")
                if mis_threads:
                    logger.info(f"Removed thread(s): {mis_threads}")
                logger.info(f"all thread(s):     {x}")
                old_x = x
            #if i == 5:
                #logger.info("terminating")
                #cfg['ThreadManager'].stop_all()
                #os._exit(0)
            time.sleep(cfg['mainloop_sleep'])
            logger.info("Mainloop cycle done.")
    except KeyboardInterrupt:
        reg.save_registry(devices[0])
        logging.info("CTRL+C pressed – terminate Threads…")
        cfg['ThreadManager'].stop_all()

