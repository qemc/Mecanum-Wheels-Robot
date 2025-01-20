import serial


class CommandHandler:
    
    def __init__(self, 
                 baudrate = 115200,
                 port = '/dev/ttyACM1'):
        
        self.baudrate = baudrate
        self.port = port
        self.conn = serial.Serial(self.port, self.baudrate, timeout=1)
        
    def sendData(self, _data):
        
        data = f"{_data}"
        self.conn.write(data.encode('utf-8'))

    def setFLSpeed(self, fl):
        command = f'SET_SPEED_MOTOR_0:RPM:{fl};\n'
        self.sendData(command)
        print(command)
        
        
    def setFRSpeed(self, fr):
        command = f'SET_SPEED_MOTOR_1:RPM:{fr};\n'
        self.sendData(command)
        print(command)
        
        
    def setRLSpeed(self, rl):
        command = f'SET_SPEED_MOTOR_2:RPM:{rl};\n'
        self.sendData(command)
        print(command)
        
        
    def setRRSpeed(self, rr):
        command = f'SET_SPEED_MOTOR_3:RPM:{rr};\n'
        self.sendData(command)
        print(command)
        
        
    def sendPIDCommand(self, motor, kp, ki, kd):
        command = f"SET_PID_MOTOR_{motor};Kp:{kp};Ki:{ki};Kd:{kd};\n"
        self.sendData(command)
        
        
    def sendSpeedCommand(self, fl, fr, rl, rr):
        
        self.setFLSpeed(fl)
        self.setFRSpeed(fr)
        self.setRLSpeed(rl)
        self.setRRSpeed(rr)
        
        print("speeds have been set")
        
    def readUART(self):

        data = self.conn.readline()
        decoded_data = data.decode('utf-8').strip()
        print(decoded_data)
        return decoded_data
