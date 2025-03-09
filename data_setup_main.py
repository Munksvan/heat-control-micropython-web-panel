import ujson as json
import time

#open JSON file and load valve_state
try:
    with open('savedata.json', 'r') as f:
        data = json.load(f)
        valve_state= data["valveOpenPercent"]
except:
    valve_state= 100
    print("valveOpenPercent variable not found. Starting with value 100.")
    
jsonData = {"valveOpenPercent": valve_state}

# Save valve_state to JSON file
def save_valve_state(state):
    jsonData["valveOpenPercent"]=state
    try:
        with open('savedata.json', 'w') as f:
            json.dump(jsonData, f)
    except:
        print("Could not save savedata.json.")

#Turn LED on/off depending on the state read from JSON file.
led.value(valve_state)

#Loop
while True:

        save_valve_state(valve_state)
    time.sleep(0.3)