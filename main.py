import time
import json
from pico_web_server import PicoWebServer
from template import Template
from IoHandler import IoHandler

# Skapa webbserver och mallinstans
server = PicoWebServer()
template = Template()

# Skapa I/O-hanterare
io_handler = IoHandler()
valves = io_handler.get_valves()

# Ladda savedata.json vid start
try:
    with open("savedata.json", "r") as f:
        savedata = json.load(f)
except:
    savedata = {
        "sensors": [
            {"id": io_handler.device_id_water_return_sensor, "name": "Water Return"},
            {"id": io_handler.device_id_outdoor_sensor, "name": "Outdoor"}
        ],
        "valves": {}
    }

# Hantera root-sidan
def handle_root(request, response):
    global valves, savedata, io_handler
    for valve in valves:
        valve.update_position()  # Uppdatera positionen för varje ventil
    sensors = [{"name": s["name"], "value": io_handler.get_temp(s["id"])} for s in savedata["sensors"]]
    html_page = template.render(
        "control_panel.html",
        {
            "title": "Pi Pico Control Panel",
            "sensors": sensors,
            "valves": [{"id": v.valve_id, "position": v.get_position()} for v in valves]
        }
    )
    response.headers["Content-Type"] = "text/html"
    yield from response.awrite(html_page)

# Hantera kommandon
def handle_command(request, response):
    global valves
    command = request.params.get("command", "")
    for valve in valves:
        if command == f"open_{valve.valve_id}":
            valve.open()
        elif command == f"close_{valve.valve_id}":
            valve.close()
        elif command == f"stop_{valve.valve_id}":
            valve.stop()
    yield from response.awrite("OK")

# Hantera konfigurationssida
def handle_config(request, response):
    global savedata, io_handler
    all_sensor_ids = io_handler.scan_sensors()  # Hämta alla anslutna sensorer
    # Konvertera binära ID:n till strängar för visning
    detected_sensors = [{"id": sensor_id.hex(), "name": next((s["name"] for s in savedata["sensors"] if s["id"] == sensor_id), "")} for sensor_id in all_sensor_ids]
    html_page = template.render(
        "config_page.html",
        {
            "title": "Configuration",
            "detected_sensors": detected_sensors
        }
    )
    response.headers["Content-Type"] = "text/html"
    yield from response.awrite(html_page)

# Spara konfiguration
def handle_save_config(request, response):
    global savedata
    sensor_ids = request.params.getlist("sensor_id[]")
    sensor_names = request.params.getlist("sensor_name[]")
    # Konvertera sträng-ID:n tillbaka till binära
    savedata["sensors"] = [{"id": bytes.fromhex(sid), "name": sname} for sid, sname in zip(sensor_ids, sensor_names) if sname]
    with open("savedata.json", "w") as f:
        json.dump(savedata, f, default=lambda x: x.hex() if isinstance(x, bytes) else x)
    yield from response.awrite("Config saved")

# Lägg till rutter
server.add_route(b"/", handle_root)
server.add_route(b"/command", handle_command)
server.add_route(b"/config", handle_config)
server.add_route(b"/save_config", handle_save_config, methods=["POST"])

# Starta servern
server.start()