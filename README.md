# Maxon EPOS4 Python

Using Python to send commands to a Maxon EPOS4 using Maxon's dynamic link library.

Run the `EPOS4.py` script in `src/` folder from root of workspace, it will by default run the following code:

```python
motor_ctrl = EPOS4()

print("Starting...")
motor_ctrl.open_port()
motor_ctrl.enable_device()

print("Moving...")
motor_ctrl.get_position()
motor_ctrl.cyclic_mode()
motor_ctrl.get_position_is()

print("Closing...")
motor_ctrl.disable_device()
motor_ctrl.close_port()
```

Cyclic mode will spin the motor from position `20000` to `-20000` 10 times. 