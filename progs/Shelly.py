# https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/Shelly

# answer for http://192.168.2.139/rpc/Shelly.GetComponents
{
    "components": [
    {
        "key": "ble",
        "status": {},
        "config": {
            "enable": false,
            "rpc": {
                "enable": true
            },    
            "observer": {
                "enable": false
            }
        }
    },
    {
        "key": "cloud",
        "status": {
            "connected": true
        },
        "config": {
            "enable": true,
            "server": "shelly-116-eu.shelly.cloud:6022/jrpc"
        }
    },
    {
        "key": "input:0",
        "status": {
            "id": 0,
            "state": false
        },
        "config": {
            "id": 0,
            "name": null,
            "type": "switch",
            "enable": true,
            "invert": false,
            "factory_reset": true
        }
    },
    {
        "key": "mqtt",
        "status": {
            "connected": false
        },
        "config": {
            "enable": false,
            "server": null,
            "client_id": "shellyplus1-e465b8f0f750",
            "user": null,
            "ssl_ca": null,
            "topic_prefix": "shellyplus1-e465b8f0f750",
            "rpc_ntf": true,
            "status_ntf": false,
            "use_client_cert": false,
            "enable_rpc": true,
            "enable_control": true
        }
    },
    {
        "key": "switch:0",
        "status": {
            "id": 0,
            "source": "SHC",
            "output": false,
            "temperature": {
                "tC": 53.4,
                "tF": 128.1
            }
        },
        "config": {
            "id": 0,
            "name": null,
            "in_mode": "follow",
            "initial_state": "match_input",
            "auto_on": false,
            "auto_on_delay": 60.00,
            "auto_off": false,
            "auto_off_delay": 60.00
        }
      },
      {
        "key": "sys",
        "status": {
            "mac": "E465B8F0F750",
            "restart_required": false,
            "time": "16:37",
            "unixtime": 1721399825,
            "uptime": 3147,
            "ram_size": 247144,
            "ram_free": 141732,
            "fs_size": 458752,
            "fs_free": 135168,
            "cfg_rev": 13,
            "kvs_rev": 0,
            "schedule_rev": 0,
            "webhook_rev": 0,
            "available_updates": {
                "beta": {
                    "version": "1.4.0-beta2"
                }
            },
            "reset_reason": 3
        },
        "config": {
            "device": {
                "name": null,
                "mac": "E465B8F0F750",
                "fw_id": "20240625-122558/1.3.3-gbdfd9b3",
                "discoverable": true,
                "eco_mode": false,
                "addon_type": null
            },
        "location": {
            "tz": "Europe/Berlin",
            "lat": 52.311000,
            "lon": 9.610500
        },
        "debug": {
            "level": 2,
            "file_level": null,
            "mqtt": {
                "enable": false
            },
            "websocket": {
                "enable": false
            },
            "udp": {
                "addr": null
            }
        },
        "ui_data": {},
        "rpc_udp": {
            "dst_addr": null,
            "listen_port": null
        },
        "sntp": {
            "server": "time.google.com"
        },
        "cfg_rev": 13
        }
    },
    {
        "key": "wifi",
        "status": {
            "sta_ip": "192.168.2.139",
            "status": "got ip",
            "ssid": "janzneu",
            "rssi": -62
        },
        "config": {
            "ap": {
                "ssid": "ShellyPlus1-E465B8F0F750",
                "is_open": true,
                "enable": false,
                "range_extender": {
                    "enable": false
                }
            },
            "sta": {
                "ssid": "janzneu",
                "is_open": false,
                "enable": true,
                "ipv4mode": "dhcp",
                "ip": null,
                "netmask": null,
                "gw": null,
                "nameserver": null
            },
            "sta1": {
                "ssid": null,
                "is_open": true,
                "enable": false,
                "ipv4mode": "dhcp",
                "ip": null,
                "netmask": null,
                "gw": null,
                "nameserver": null
            },
            "roam": {
                "rssi_thr": -80,
                "interval": 60
            }
        }
    }
    ],
    "cfg_rev": 13,
    "offset": 0,
    "total": 8
}


#answer for http://192.168.2.139/rpc/Sys.GetStatus
{
    "mac":"E465B8F0F750",
    "restart_required":false,
    "time":"17:52",
    "unixtime":1721404321,
    "uptime":7644,
    "ram_size":247168,
    "ram_free":143112,
    "fs_size":458752,
    "fs_free":135168,
    "cfg_rev":13,
    "kvs_rev":0,
    "schedule_rev":0,
    "webhook_rev":0,
    "available_updates":{
        "beta":{
            "version":"1.4.0-beta2"
        }
    },
    "reset_reason":3
}