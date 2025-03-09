import utime
from RequestParser import RequestParser
import json
import uasyncio
# import _thread
# from ResponseBuilder import ResponseBuilder
from WiFiConnection import WiFiConnection
from IoHandler import IoHandler
import random
import utime

class ValveTimer:
    open_procent = 100.0
    valve_delta_time = 20
    last_value = -5
    start = 0
    opentime = 0
    
    def __init__(self):
        # get everything into a starting state
        self.__class__.get_stored_valve_position()
        self.open_procent = IoHandler.load_valve_state_from_file("open_procent")
        self.valve_delta_time = IoHandler.load_valve_state_from_file("valve_delta_time")
        self.start = int(utime.ticks_ms())
        self.opentime = open_procent*valve_delta_time/100

    @classmethod
    def get_stored_valve_position(cls, valve_open, valve_closed):
        
        # stuff goes here
        end = int(utime.ticks_ms())
        runtime = utime.ticks_diff(end, start)/1000
        if not valve_open:
            #opening
            if opentime < valve_delta_time:
                opentime = opentime + runtime
            else:
                opentime = valve_delta_time
        elif not valve_closed:
            #closeing
            if opentime > 0:
                opentime = opentime - runtime
            else:
                opentime = 0
        open_procent = (opentime *100)/valve_delta_time
        if last_value != open_procent and open_procent <= 100.0 and open_procent >= 0:
            last_value = open_procent
            print("Open: " + str(open_procent) + "%%")
            save_success = IoHandler.save_valve_state_to_file(open_procent)
        start = int(utime.ticks_ms())
        return open_procent
    
