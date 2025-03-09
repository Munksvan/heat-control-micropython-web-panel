from machine import Pin 
import onewire, ds18x20, time
import binascii

class DS18b20Module:
    def __init__(self, pin_number):
        self.ds_pin = Pin(pin_number)
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.ds_pin))
        self.values = dict()
        self.dictionaryToAdd = dict()

    
    def get_temp_reading(self, device_id):
        roms = self.ds_sensor.scan()
        if not roms:
            raise RuntimeError("Found no DS18b20")
        self.ds_sensor.convert_temp()
        time.sleep_ms(750)
#        temp = self.ds_sensor.read_temp(roms[0])
        temp = 99999
        for rom in roms:
            if rom == device_id:
                temp = self.ds_sensor.read_temp(rom)
        if temp == 99999:
            print('Found DS devices: ', roms)
            raise RuntimeError("Did not find onewire temp device : " + device_id) 
#        print(f"Temperature is {temp}")
        return temp

    def get_temp_readings(self):
        roms = self.ds_sensor.scan()
        if not roms:
            raise RuntimeError("Found no DS18b20")
        self.ds_sensor.convert_temp()
        time.sleep_ms(750)
        for rom in roms:
            s = binascii.hexlify(rom)
            readable_string = s.decode('ascii')
            self.values[readable_string] = self.ds_sensor.read_temp(rom)
#         print(f"Temperaturemodule is {self.values}")
        return self.values