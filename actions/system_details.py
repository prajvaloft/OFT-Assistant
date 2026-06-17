# system_details.py

import platform
import socket
import requests
import psutil


def get_system_details(detail_type="all"):
    try:

        if detail_type == "location":

            data = requests.get(
                "https://ipinfo.io/json",
                timeout=5
            ).json()

            return {
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country"),
                "ip": data.get("ip"),
                "loc": data.get("loc")
            }

        elif detail_type == "battery":

            battery = psutil.sensors_battery()

            if battery:
                return {
                    "battery_percent": battery.percent,
                    "plugged_in": battery.power_plugged
                }

            return {
                "battery": "Not Available"
            }

        elif detail_type == "ram":

            ram = psutil.virtual_memory()

            return {
                "total_gb": round(ram.total / (1024 ** 3), 2),
                "available_gb": round(ram.available / (1024 ** 3), 2),
                "used_percent": ram.percent
            }

        elif detail_type == "cpu":

            return {
                "cpu": platform.processor(),
                "usage_percent": psutil.cpu_percent(interval=1),
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True)
            }

        elif detail_type == "disk":

            disk = psutil.disk_usage("/")

            return {
                "total_gb": round(disk.total / (1024 ** 3), 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "used_percent": disk.percent
            }

        elif detail_type == "wifi":

            return {
                "hostname": socket.gethostname(),
                "local_ip": socket.gethostbyname(socket.gethostname())
            }

        elif detail_type == "ip":

            data = requests.get(
                "https://ipinfo.io/json",
                timeout=5
            ).json()

            return {
                "public_ip": data.get("ip")
            }

        else:

            return {
                "os": platform.system(),
                "os_version": platform.version(),
                "machine": platform.machine(),
                "hostname": socket.gethostname(),
                "cpu": platform.processor(),
                "cpu_usage": psutil.cpu_percent(interval=1),
                "ram_gb": round(
                    psutil.virtual_memory().total / (1024 ** 3),
                    2
                ),
                "ram_usage": psutil.virtual_memory().percent,
                "local_ip": socket.gethostbyname(
                    socket.gethostname()
                )
            }

    except Exception as e:
        return {
            "error": str(e)
        }