# class to handle the IO for the demo setup
from machine import Pin, ADC
import neopixel
import time
import onewire, ds18x20
from ds18b20_module import DS18b20Module
import ujson as json



class IoHandler:
   # temp sensor
    temp = ADC(4)
    temp_value = 0  
    
    #onewire temp sensors
    ds_pin = Pin(22)
    return_sensor = DS18b20Module(ds_pin)
    onewire_temp = 0
    onewire_temps = dict()

    # coloured leds
    open_valve = Pin(16, Pin.OUT)
    close_valve = Pin(17, Pin.OUT)
    open_valve.value(1)
    close_valve.value(1)
    coloured_states = [1, 1]
    
    #file
    save_success = True
    valve_state = 100.0
    jsonData = {"valveOpenPercent": valve_state, "valve2OpenPercent": valve_state }
#     jsonData = {"valveOpenPercent": valve_state}

    def __init__(self):
        # get everything into a starting state
        self.__class__.get_pot_reading()
        self.__class__.show_coloured_valves()
        self.__class__.get_onewire_temps()
#         self.__class__.clear_rgb_valves()

    # output, setters and getters for coloured leds
    @classmethod
    def show_coloured_valves(cls):
        cls.open_valve.value(cls.coloured_states[0])
        cls.close_valve.value(cls.coloured_states[1])

    @classmethod
    def set_coloured_valves(cls, states):
        try:
            cls.set_open_valve(states[0])
            cls.set_close_valve(states[1])
        except:
            pass
        cls.show_coloured_valves()

    @classmethod
    def set_open_valve(cls, state):
        cls.coloured_states[0] = 0 if state == 1 else 1

    @classmethod
    def set_close_valve(cls, state):
        cls.coloured_states[1] = 0 if state == 1 else 1

    @classmethod
    def get_open_valve(cls):
        return 0 if cls.coloured_states[0] == 0 else 1

    @classmethod
    def get_close_valve(cls):
        return 0 if cls.coloured_states[1] == 0 else 1



    
    @classmethod
    def get_onewire_temp(cls, device_id):
        cls.onewire_temp = cls.return_sensor.get_temp_reading(device_id)
#        print(f"Temperature2 is {cls.onewire_temp}")
        return cls.onewire_temp

    @classmethod
    def get_onewire_temps(cls):
#         cls.onewire_temps.clear()
        cls.onewire_temps.update(cls.return_sensor.get_temp_readings())
#         print(f"Temperature2 is {cls.onewire_temps}")
        return cls.onewire_temps
   # temp handler
    @classmethod
    def get_temp_reading(cls):
        temp_voltage = cls.temp.read_u16() * (3.3 / 65535)
        cls.temp_value = 27 - (temp_voltage - 0.706) / 0.001721
        return cls.temp_value

    @classmethod
    def save_valve_state_to_file(cls, state):
        cls.jsonData["valveOpenPercent"]=state
        cls.jsonData["valve2OpenPercent"]=state
        try:
            with open('savedata.json', 'w') as f:
                json.dump(cls.jsonData, f)
            cls.save_success = True
        except:
            print("Could not save savedata.json.")
            cls.save_success = False
        return cls.save_success


#open JSON file and load valve_state
    @classmethod
    def load_valve_state_from_file(cls):
        try:
            with open('savedata.json', 'r') as f:
                data = json.load(f)
                cls.valve_state= data["valveOpenPercent"]
        except:
            cls.valve_state= 100
            print("valveOpenPercent variable not found. Starting with value 100.")
        return cls.valve_state