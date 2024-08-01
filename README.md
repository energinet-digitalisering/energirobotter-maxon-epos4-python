# Maxon EPOS4 Python

Using `Python3` and the library `ctypes` to send commands to a Maxon EPOS4 using Maxon's dynamic link library. 

Many of the functions are from [this](https://support.maxongroup.com/hc/en-us/articles/360012695739-EPOS2-EPOS4-IDX-Commanding-by-Python-ctypes) tutorial. See the [docs](https://github.com/energinet-digitalisering/maxon-epos4-python/blob/main/docs/Maxon%20EPOS%20command%20library.pdf) for the full list of possible functions in the dynamic link library.

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