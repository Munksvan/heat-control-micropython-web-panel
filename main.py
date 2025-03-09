# full demo with web control panel
# combines multi core and multi tasking

import utime
from RequestParser import RequestParser
import json
import uasyncio
import _thread
from ResponseBuilder import ResponseBuilder
from WiFiConnection import WiFiConnection
from IoHandler import IoHandler

# connect to WiFi
if not WiFiConnection.start_station_mode(True):
    raise RuntimeError('network connection failed')


async def handle_request(reader, writer):
    try:
        raw_request = await reader.read(2048)

        request = RequestParser(raw_request)

        response_builder = ResponseBuilder()
        # filter out api request
        if request.url_match("/api"):
            action = request.get_action()
            temp_dict = dict()
            device_id_water_return_sensor = "2870bd81e3e13cfc"
            device_id_outdoor_sensor = "28ac0081e3e13ce6"
            if action == 'readPot':
                # ajax request for potentiometer data
                # used in simple test
                temp_dict.update(IoHandler.get_onewire_temps())
                return_temp_value = temp_dict[device_id_water_return_sensor]
                temp_value = temp_dict[device_id_outdoor_sensor]
                # send back reading as simple text
                response_builder.set_body(return_temp_value)
            elif action == 'readData':
                # ajax request for data
                temp_dict.update(IoHandler.get_onewire_temps())
                temp_value = temp_dict[device_id_water_return_sensor]
                return_temp_value = IoHandler.get_temp_reading()
                #print(f"Temperature4 is {return_temp_value}")
                cled_states = {
                    'open': IoHandler.get_open_valve(),
                    'close': IoHandler.get_close_valve()
                }
                response_obj = {
                    'status': 0,
                    'return_temp_value': return_temp_value,
                    'temp_value': temp_value,
                    'cled_states': cled_states,
                }
                response_builder.set_body_from_dict(response_obj)
            elif action == 'setLedColour':
                # turn on requested coloured led
                # returns json object with led states
                valve_action = request.data()['colour']

                status = 'OK'
                cled_states = {
                    'open': 0,
                    'close': 0
                }
                if valve_action == 'open':
                    cled_states['open'] = 1
                elif valve_action == 'close':
                    cled_states['close'] = 1
                elif valve_action == 'hold':
                    # hold valve at position
                    pass
                else:
                    status = 'Error'
                IoHandler.set_coloured_valves([cled_states['open'], cled_states['close']])
                response_obj = {
                    'status': status,
                    'cled_states': cled_states
                }
                response_builder.set_body_from_dict(response_obj)
            else:
                # unknown action
                response_builder.set_status(404)

        # try to serve static file
        else:
            response_builder.serve_static_file(request.url, "/api_index.html")

        response_builder.build_response()
        writer.write(response_builder.response)
        await writer.drain()
        await writer.wait_closed()

    except OSError as e:
        print('connection error ' + str(e.errno) + " " + str(e))


async def main():
    print('Setting up webserver...')
    server = uasyncio.start_server(handle_request, "0.0.0.0", 80)
    uasyncio.create_task(server)

    # main async loop on first core
    # just pulse the red led
    counter = 0
    while True:
#         if counter % 500 == 0:
#             IoHandler.toggle_red_valve()
#         counter += 1
        await uasyncio.sleep(0)

# run the top 4 neopixel scrolling loop
def second_core_valve_control():
    valve_delta_time = 20
    start = int(utime.ticks_ms())
    last_value = -5
    open_procent = IoHandler.load_valve_state_from_file()
    opentime = open_procent*valve_delta_time/100
    while True:
        # stuff goes here
        end = int(utime.ticks_ms())
        runtime = utime.ticks_diff(end, start)/1000
        if not IoHandler.get_open_valve():
            #opening
            if opentime < valve_delta_time:
                opentime = opentime + runtime
            else:
                opentime = valve_delta_time
        elif not IoHandler.get_close_valve():
            #closeing
            if opentime > 0:
                opentime = opentime - runtime
            else:
                opentime = 0
#             print("Closing: ")
#         else:
#             print("Time: " + str(runtime))
        open_procent = (opentime *100)/valve_delta_time
        if last_value != open_procent and open_procent <= 100.0 and open_procent >= 0:
            last_value = open_procent
            print("Open: " + str(open_procent) + "%%")
            save_success = IoHandler.save_valve_state_to_file(open_procent)
        start = int(utime.ticks_ms())
        utime.sleep(0.2)
 
# start neopixel scrolling loop on second processor
second_thread = _thread.start_new_thread(second_core_valve_control, ())

try:
    # start asyncio tasks on first core
    uasyncio.run(main())
finally:
#     save_success = IoHandler.save_valve_state_to_file(open_procent)
#     print("save: " + save_success)
    print("running finally block")
    uasyncio.new_event_loop()
