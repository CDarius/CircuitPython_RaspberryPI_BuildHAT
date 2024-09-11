import board
import asyncio
from buildhat.hat import Hat
from buildhat.motors.speedunit import SpeedUnit
from buildhat.motors.direction import Direction

motor_port = 3

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

async def data_loop(hat):
    motor = buildhat.get_device(motor_port)
    motor.data_update_interval =  10

    while not stop:
        if motor.has_absolute_position:
            print(f"Speed: {motor.actual_speed} °/s, Pos: {motor.actual_position}°, APos: {motor.actual_absolute_position}°")
        else:
            print(f"Speed: {motor.actual_speed} °/s, Pos: {motor.actual_position}°")
        await asyncio.sleep(0.1)

async def motor_loop(hat):
    motor = buildhat.get_device(motor_port)
    
    motor.power_limit = 1
    motor.release_after_run = True # The motor is free to spin after the movement is done

    while not stop:
        motor.run_command_speed_unit = SpeedUnit.DGS # degrees per second
        motor.run_command_default_speed = 120 # Default speed when not specified in the run command
        await motor.run_for_rotations(2) # Use default speed (90 DGS)
        await motor.run_for_rotations(2, speed = 180) # Run at speed 4180 DGS
        await motor.run_for_degrees(90) # Turn 90 degree from current position 
        await motor.run_for_degrees(-90, speed = 180) # Turn back 90 degree from current postion

        motor.actual_position = 0 # Preset actual_position and change it to 0
        await motor.run_to_position(720, speed=360) # Run the motor at the position 720 degree

        motor.run_command_speed_unit = SpeedUnit.RPM # revolutions per second
        if motor.has_absolute_position:
            # Not all motors have the absolute position
            # Absolute position cover one turn from -180 to 180 degree            
            await motor.run_to_absolute_angle(0, speed = 60)
            await motor.run_to_absolute_angle(-30, speed = 120, direction=Direction.CW)
            await motor.run_to_absolute_angle(-170, speed = 90, direction=Direction.CCW)
            await motor.run_to_absolute_angle(170, speed = 120, direction=Direction.SHORTEST)

        await motor.run_for_seconds(5) # Spin the motor for 5 seconds
        motor.start(speed = 120) # Start the motor to run indefinitely
        await asyncio.sleep(2)
        motor.stop() # Stop and leaving floating
        await asyncio.sleep(1)
        
        motor.pwm(1) # Spin the motor open loop at max speed. All previous mode were close loop
        await asyncio.sleep(2)
        motor.coast() # Let the motor coast to a stop
        await asyncio.sleep(2)
        
        motor.reverse_direction = not motor.reverse_direction
        
async def main():
    buildhat_loop_task = asyncio.create_task(buildhat_loop(buildhat))
    data_loop_task = asyncio.create_task(data_loop(buildhat))
    motor_loop_task = asyncio.create_task(motor_loop(buildhat))
    
    await asyncio.gather(buildhat_loop_task, data_loop_task, motor_loop_task)
    
asyncio.run(main())
