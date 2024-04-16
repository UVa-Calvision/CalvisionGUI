import serial
import time
class A7585D_REG:
    HV_ENABLE = 0
    CNTRL_MODE = 1
    V_TARGET = 2
    RAMP = 3
    MAX_V = 4
    MAX_I = 5
    MAX_T = 6
    CAL_TEMP_M2 = 7
    CAL_TEMP_M = 8
    CAL_TEMP_Q = 9
    ALFA_VOUT = 10
    ALFA_IOUT = 11
    ALFA_VREF = 12
    ALFA_TREF = 13
    T_COEF_SIPM = 28
    LUT_ENABLE = 29
    ENABLE_PI = 30
    EMERGENCY_STOP = 31
    IZERO = 32
    LUT_ADDRESS = 36
    LUT_PROGRAM_V = 37
    LUT_PROGRAM_T = 38
    LUT_LENGTH = 39
    I2C_BASE_ADDRESS = 40
    CURRENT_RANGE = 81

    MON_VIN=230
    MON_VOUT=231
    MON_IOUT=232
    MON_VREF=233
    MON_TREF=234
    MON_VTARGET=235
    MON_RTARGET=236
    MON_CVT=237
    MON_COMPLIANCE_V = 249
    MON_COMPLIANCE_I = 250

    PRODUCT_CODE=251
    FW_VERSION=252
    HW_VERSION=253
    SERIAL_NUMBER=254

class A7585D:
    def __init__(self):
        self.ser=None

    def open(self, serial_port):
        self.ser = serial.Serial(serial_port, 115200, timeout=1)
        self.ser.write(b"\r\n")
        self.ser.write(b"\r\n")
        time.sleep(0.1)
        send_string = "AT+MACHINE\r\n"
        self.ser.write(bytes(send_string.encode("utf-8")))
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.flushOutput()
        time.sleep(1)
    
    def set_parameter(self, param, value):
        send_string = "AT+SET," + str(param) + "," + str("{:.9f}".format(value)) +"\r\n"
        self.ser.write(bytes(send_string.encode("utf-8")))
        res = str(self.ser.readline())
        time.sleep(0.01)
        if "OK" in res:
            return True
        else:
            raise Exception('set', 'error')        


    def get_parameter(self, param):
        send_string = "AT+GET," + str(int(param)) + "\r\n"
        self.ser.write(bytes(send_string.encode("utf-8")))
        res = str(self.ser.readline(),'ascii')
        if "OK" in res:
            a=res.split("=")
            ab=a[1].replace("\\r","").replace("\\n","")
            return float(ab)
        else:
            raise Exception('get', 'error')       

    def save_parameter(self):
        send_string = "AT+SET,255,1\r\n"
        self.ser.write(bytes(send_string.encode("utf-8")))
        time.sleep(2)
        res = str(self.ser.readline())
        if "OK" in res:
            return True
        else:
            raise Exception('set', 'error') 

    def close(self):
        self.ser.close()