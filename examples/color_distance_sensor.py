'''
Test code for Boost color & distance sensor
Part number: 88007
'''

import board
import asyncio
from buildhat.hat import Hat
from buildhat.devices.color import Color

sensor_port = 1

# Pins for Waveshare RP2040-Zero.
# Change the pins if you are using a different board
tx_pin = board.TX
rx_pin = board.RX
reset_pin = board.GP23

buildhat = Hat(tx=tx_pin, rx=rx_pin, reset=reset_pin, debug=True)

stop = False
async def buildhat_loop(hat):
    while not stop:
        hat.update()
        await asyncio.sleep(0)

async def read_loop(hat):
    sensor = buildhat.get_device(sensor_port)
 
    while not stop:
        color = await sensor.get_color()
        print(f"Color: {color}")
        ambient_light = await sensor.get_ambient_light()
        print(f"Ambient light: {ambient_light}")
        reflected = await sensor.get_reflected_light()
        print(f"Reflected light: {reflected}")
        distance = await sensor.get_distance()
        print(f"Distance: {distance}")
        counter = await sensor.get_counter()
        print(f"Counter: {counter}")

        sensor.off()
        print(f"Sensor off")
        await asyncio.sleep(1)
        sensor.on()
        print(f"Sensor on")
        await asyncio.sleep(1)

async def main():
    buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
    read_loop_task = asyncio.create_task(read_loop(buildhat))
    
    await asyncio.gather(buildhat_loop_task, read_loop_task)
    
asyncio.run(main())
