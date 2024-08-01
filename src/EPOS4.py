import ctypes
import time


class EPOS4:
    def __init__(self):
        # Get EPOS4 dynamic link library functions
        path = "lib/EposCmd64.dll"
        ctypes.cdll.LoadLibrary(path)
        self.epos = ctypes.CDLL(path)

        self.node_id = 1  # Node ID must match with Hardware Dip-Switch setting of EPOS4
        self.keyhandle = 0

    def eval_error_pass(self, p_error_code):
        p_error_info = " " * 40

        if p_error_code.value != 0x0:
            self.epos.VCS_GetErrorInfo(p_error_code.value, p_error_info, 40)
            print("Error Code %#5.8x" % p_error_code.value)
            print("Description: %s" % p_error_info)
            return False

        # No Error
        else:
            return True

    # Check Error State of EPOS4
    def device_error_pass(self):
        p_error_code = ctypes.c_uint()
        p_device_error_code = ctypes.c_uint()

        self.epos.VCS_GetDeviceErrorCode(
            self.keyhandle,
            self.node_id,
            1,
            ctypes.byref(p_device_error_code),
            ctypes.byref(p_error_code),
        )

        if p_device_error_code.value == 0:
            self.eval_error_pass(p_error_code)
            return True

        else:
            print("Device Error: %#5.8x" % p_device_error_code.value)
            print("For more information see Firmware Specification")
            return False

    def open_port(self):
        print("node_id: %d" % self.node_id)
        p_error_code = ctypes.c_uint()

        # Open USB Port
        self.keyhandle = self.epos.VCS_OpenDevice(
            b"EPOS4",
            b"MAXON SERIAL V2",
            b"USB",
            b"USB0",
            ctypes.byref(p_error_code),
        )

        if self.keyhandle != 0:
            print("Keyhandle: %8d" % self.keyhandle)
            return True

        else:
            print("Could not open COM-Port")
            self.eval_error_pass(p_error_code)
            return False

    def close_port(self):
        p_error_code = ctypes.c_uint()

        ret = self.epos.VCS_CloseDevice(self.keyhandle, ctypes.byref(p_error_code))

        if ret == 1:
            self.eval_error_pass(p_error_code)
            return True
        else:
            print("Error CloseDevice")
            return False

    def enable_device(self):
        pls_enabled = ctypes.c_bool()
        p_error_code = ctypes.c_uint()

        # Set Operation Mode PPM
        ret = self.epos.VCS_ActivateProfilePositionMode(
            self.keyhandle, self.node_id, ctypes.byref(p_error_code)
        )

        # Profile Velocity=500rpm / Acceleration=1000rpm/s / Deceleration=1000rpm/s
        ret = self.epos.VCS_SetPositionProfile(
            self.keyhandle, self.node_id, 500, 1000, 1000, ctypes.byref(p_error_code)
        )

        # Check Device Error before enabling
        if self.device_error_pass():
            # Enable Device
            ret = self.epos.VCS_SetEnableState(
                self.keyhandle, self.node_id, ctypes.byref(p_error_code)
            )

            if ret == 1:
                if self.eval_error_pass(p_error_code):
                    # Check if Device is Enabled
                    self.epos.VCS_GetEnableState(
                        self.keyhandle,
                        self.node_id,
                        ctypes.byref(pls_enabled),
                        ctypes.byref(p_error_code),
                    )

                    if pls_enabled.value == 1:
                        print("Device Enabled")
                        return True
                    else:
                        print("Device Not Enabled!")
                        return False
                else:
                    return False
            else:
                print("Error during enabling Device")
                return False

        # Device is in Error State
        else:
            return False

    def disable_device(self):
        pls_disabled = ctypes.c_bool()
        p_error_code = ctypes.c_uint()

        ret = self.epos.VCS_SetDisableState(
            self.keyhandle, self.node_id, ctypes.byref(p_error_code)
        )

        if ret == 1:
            if self.eval_error_pass(p_error_code):

                self.epos.VCS_GetDisableState(
                    self.keyhandle,
                    self.node_id,
                    ctypes.byref(pls_disabled),
                    ctypes.byref(p_error_code),
                )

                if pls_disabled.value == 1:
                    print("Device Disabled")
                    return True
                else:
                    print("Device could not be disabled")
                    return False
            else:
                return False
        else:
            print("Error SetDisableState")
            return False

    def get_position(self):
        # CANopen Object: Position Actual Value
        object_idx = 0x6064
        object_sub_idx = 0x00
        nr_of_bytes_to_read = 0x04
        # DWORD
        nr_of_bytes_read = ctypes.c_uint()
        # 0x6064 => INT32
        p_data = ctypes.c_int()
        p_error_code = ctypes.c_uint()

        ret = self.epos.VCS_GetObject(
            self.keyhandle,
            self.node_id,
            object_idx,
            object_sub_idx,
            ctypes.byref(p_data),
            nr_of_bytes_to_read,
            ctypes.byref(nr_of_bytes_read),
            ctypes.byref(p_error_code),
        )

        if ret == 1:
            print("Position Actual Value: %d [inc]" % p_data.value)
            return p_data.value
        else:
            print("GetObject failed")
            return False

    # Get Position direct via function
    def get_position_is(self):
        p_data = ctypes.c_long()
        p_error_code = ctypes.c_uint()

        ret = self.epos.VCS_GetPositionIs(
            self.keyhandle,
            self.node_id,
            ctypes.byref(p_data),
            ctypes.byref(p_error_code),
        )

        if ret == 1:
            print("Position Actual Value: %d [inc]" % p_data.value)
            return p_data.value
        else:
            print("GetPositionIs failed")
            return False

    # Read Statusword and mask it to bit12
    def wait_acknowledged(self):
        object_idx = 0x6041
        object_sub_idx = 0x0
        nr_of_bytes_to_read = 0x02
        nr_of_bytes_read = ctypes.c_uint()
        p_data = ctypes.c_uint()
        p_error_code = ctypes.c_uint()

        # Setpoint Acknowledged
        mask_bit12 = 0x1000
        bit12 = 0
        i = 0

        while True:
            # Read Statusword
            self.epos.VCS_GetObject(
                self.keyhandle,
                self.node_id,
                object_idx,
                object_sub_idx,
                ctypes.byref(p_data),
                nr_of_bytes_to_read,
                ctypes.byref(nr_of_bytes_read),
                ctypes.byref(p_error_code),
            )
            bit12 = mask_bit12 & p_data.value

            # Timed out
            if i > 20:
                return False

            if bit12 == mask_bit12:
                time.sleep(1)
                i += 1

            # bit12 reseted = new profile started
            else:
                return True

    def cyclic_mode(self):

        p_error_code = ctypes.c_uint()

        print("Wait finishing positioning...")

        for x in range(1, 11):
            print("Loop: %d" % x)

            # TargetPosition=20'000qc / AbsolutMovement=0 =>Relative Positioning / StartProfileImmediately=0
            self.epos.VCS_MoveToPosition(
                self.keyhandle, self.node_id, 20000, 0, 0, ctypes.byref(p_error_code)
            )

            self.wait_acknowledged()

            # Send new profile during execution of previous profile
            self.epos.VCS_MoveToPosition(
                self.keyhandle, self.node_id, -20000, 0, 0, ctypes.byref(p_error_code)
            )

            self.wait_acknowledged()

        print("Cyclic movemenent finished")

        return True

    def set_position(self, pos):

        p_error_code = ctypes.c_uint()

        self.epos.VCS_MoveToPosition(
            self.keyhandle, self.node_id, pos, 0, 0, ctypes.byref(p_error_code)
        )

        self.wait_acknowledged()

        print("Movemenent finished")

        return True


if __name__ == "__main__":

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
