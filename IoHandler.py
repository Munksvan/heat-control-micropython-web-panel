from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20
from valve import Valve

class IoHandler:
    def __init__(self):
        # Temperatursensorer
        self.sensor_pin = Pin(22, Pin.IN)  # Pin för OneWire-bussen
        self.ow = OneWire(self.sensor_pin)
        self.ds = DS18X20(self.ow)
        
        # Sensor-ID:n (exempel, kan uppdateras dynamiskt)
        self.device_id_water_return_sensor = b'(\xb2\x9e\x81\x1c\x00\x00\xce'
        self.device_id_outdoor_sensor = b'(\xff\x9e\x81\x1c\x00\x00\xab'
        
        # Ventiler (pin-nummer och ID:n)
        self.valves = [
            Valve(open_pin=12, close_pin=13, valve_id="valve1", travel_time=10),
            Valve(open_pin=14, close_pin=15, valve_id="valve2", travel_time=10),
            Valve(open_pin=16, close_pin=17, valve_id="valve3", travel_time=10),
            Valve(open_pin=18, close_pin=19, valve_id="valve4", travel_time=10),
        ]

    def get_temp(self, device_id):
        self.ds.convert_temp()
        time.sleep_ms(750)
        return self.ds.read_temp(device_id)

    def get_valves(self):
        return self.valves

    def get_sensor_ids(self):
        return [self.device_id_water_return_sensor, self.device_id_outdoor_sensor]

    def scan_sensors(self):
        """Skanna efter alla anslutna sensorer och returnera deras ID:n."""
        return self.ow.scan()
        
        
    #def print_sensor_ids(self):
    #    sensors = self.scan_sensors()
    #    for sensor in sensors:
    #        print("Sensor ID:", sensor.hex())