from microbit import i2c
from microbit import display, Image, sleep, button_a, button_b

class ServoBoard:

    PCA9685_ADDRESS = 0x40
    MODE1 = 0x00
    MODE2 = 0x01
    SUBADR1 = 0x02
    SUBADR2 = 0x03
    SUBADR3 = 0x04
    PRESCALE = 0xFE
    LED0_ON_L = 0x06
    LED0_ON_H = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09
    ALL_LED_ON_L = 0xFA
    ALL_LED_ON_H = 0xFB
    ALL_LED_OFF_L = 0xFC
    ALL_LED_OFF_H = 0xFD

    STP_CHA_L = 2047
    STP_CHA_H = 4095

    STP_CHB_L = 1
    STP_CHB_H = 2047

    STP_CHC_L = 1023
    STP_CHC_H = 3071

    STP_CHD_L = 3071
    STP_CHD_H = 1023

    initialised = False

    def i2cwrite(self, addr, reg, value):
        #  buf = pins.createBuffer(2)
        #  buf = [reg, value]
        #  buf[0] = reg
        #  buf[1] = value
        #  pins.i2cWriteBuffer(addr, buf)
        i2c.write(addr, bytes([reg, value]), repeat=False)

    def i2cread(self, addr, reg):
        #  pins.i2cWriteNumber(addr, reg, NumberFormat.UInt8BE)
        i2c.write(addr, bytes([reg]))
        #  val = pins.i2cReadNumber(addr, NumberFormat.UInt8BE)
        val = i2c.read(addr, 1)[0]
        return val

    def initPCA9685(self):
        self.i2cwrite(self, self.PCA9685_ADDRESS, self.MODE1, 0x00)
        self.setFreq(self, 50)
        self.setPwm(self, 0, 0, 4095)
        for idx in range(1, 16):
            self.setPwm(self, idx, 0, 0)
        self.initialised = True

    def setFreq(self, freq):
        # Constrain the frequency
        prescaleval = 25000000
        prescaleval /= 4096
        prescaleval /= freq
        prescaleval -= 1
        prescale = int(prescaleval)  # Math.Floor(prescaleval + 0.5)
        oldmode = self.i2cread(self, self.PCA9685_ADDRESS, self.MODE1)
        newmode = (oldmode & 0x7F) | 0x10
        self.i2cwrite(self, self.PCA9685_ADDRESS, self.MODE1, newmode)
        self.i2cwrite(self, self.PCA9685_ADDRESS, self.PRESCALE, prescale)
        self.i2cwrite(self, self.PCA9685_ADDRESS, self.MODE1, oldmode)
        sleep(1000)
        self.i2cwrite(self, self.PCA9685_ADDRESS, self.MODE1, oldmode | 0xA1)
        display.scroll('initialised')

    def setPwm(self, channel, on, off):
        if not (0 <= channel <= 15):
            return
        buf = [0] * 5
        buf[0] = self.LED0_ON_L + 4 * channel
        buf[1] = on & 0xFF
        buf[2] = (on >> 8) & 0xFF
        buf[3] = off & 0xFF
        buf[4] = (off >> 8) & 0xFF
        i2c.write(self.PCA9685_ADDRESS, bytes(buf))

    def Servo(self, channel, degree):
        if not self.initialised:
            self.initPCA9685(self)
        # 50hz: 20,000 us
        v_us = degree * 1800 / 180 + 600  # 0.6 ~ 2.4
        value = int(v_us * 4096 / 20000)
        self.setPwm(self, channel, 0, value)

    def ServoPulse(self, channel, pulse):
        if not self.initialised:
            self.initPCA9685()
        # 50hz: 20,000 us
        value = int(pulse * 4096 / 20000)
        self.setPwm(self, channel, 0, value)


theServoBoard = ServoBoard
theServoBoard.Servo(theServoBoard, 0, 0)

while True:
    if button_a.is_pressed() and button_b.is_pressed():
        theServoBoard.Servo(theServoBoard, 0, 180)
        display.show(Image.HAPPY)
    elif button_a.is_pressed():
        theServoBoard.Servo(theServoBoard, 0, 0)
        display.show(Image.SAD)
    elif button_b.is_pressed():
        theServoBoard.Servo(theServoBoard, 0, 90)
        display.show(Image.ANGRY)
    sleep(100)
