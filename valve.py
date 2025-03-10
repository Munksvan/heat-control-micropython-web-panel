import time
from machine import Pin

class Valve:
    def __init__(self, open_pin, close_pin, valve_id, travel_time=10):
        self.open_pin = Pin(open_pin, Pin.OUT)
        self.close_pin = Pin(close_pin, Pin.OUT)
        self.valve_id = valve_id
        self.travel_time = travel_time  # Tid i sekunder för att fullt öppna/stänga ventilen
        self.position = 0  # 0 = stängd, 100 = fullt öppen
        self.last_action_time = 0
        self.is_moving = False

    def open(self):
        if not self.is_moving:
            self.is_moving = True
            self.close_pin.off()
            self.open_pin.on()
            self.last_action_time = time.time()
            print(f"Opening valve {self.valve_id}")

    def close(self):
        if not self.is_moving:
            self.is_moving = True
            self.open_pin.off()
            self.close_pin.on()
            self.last_action_time = time.time()
            print(f"Closing valve {self.valve_id}")

    def stop(self):
        self.open_pin.off()
        self.close_pin.off()
        self.is_moving = False
        print(f"Stopped valve {self.valve_id}")

    def update_position(self):
        if self.is_moving:
            elapsed = time.time() - self.last_action_time
            if self.open_pin.value():
                self.position = min(100, self.position + (elapsed / self.travel_time) * 100)
            elif self.close_pin.value():
                self.position = max(0, self.position - (elapsed / self.travel_time) * 100)
            if self.position in (0, 100) or elapsed >= self.travel_time:
                self.stop()
        return self.position

    def get_position(self):
        return self.position