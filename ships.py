"""
Ship class for virtual ships simulationS
"""

import time
from math import sin,cos,pi
import threading
from socket import socket, AF_INET, SOCK_STREAM

class Ship(threading.Thread):
    """Virtual sailing ship"""
    def __init__(self, mmsi, lat, lon, course,speed, host='localhost', port=10110 ):
        threading.Thread.__init__(self)
        self.mmsi = mmsi
        self.host = host
        self.port = port
        self.lat = lat
        self.lon = lon
        self.y = lat*60
        self.x = lon*60 * cos(lat*pi/180)  # nautical miles OL
        self.course = course*pi/180 # course in rad
        self.heading = course # heading in degrees
        self.speed = speed # knots
        self.minute = 1 #60
        self.deadreckoning = True
        self.navigation = {}
        self.utc_time = None
        self.date = None
        self.day = None
        self.month = None
        self.year = None
        self.status = None

    def get_mmsi(self):
        """atribute getter"""
        return str(self.mmsi)

    def get_navigation(self):
        """atribute getter"""
        return self.navigation

    def _get_latitude(self):
        """atribute getter"""
        return self.y   # nautical miles NB

    def _get_longitude(self):
        """atribute getter"""
        return self.x # nautical miles OL

    def get_course(self):
        """atribute getter"""
        return self.course * 180/ pi # in degrees

    def set_course(self,course):
        """atribute setter"""
        self.course = course*pi/180

    def get_speed(self):
        """atribute getter"""
        return self.speed

    def run(self):
        """thread runner"""
        super().run()
        self.deadreckoning = False
        try:
            for gps in self.gps_from_signalk(host ='localhost', port=10110):
                self.navigation = gps
                #print(self.get_navigation())

        except RuntimeError as e:
            print(f'GPS stream error: {e}')
            print('Switching to dead reckoning mode')

        self.deadreckoning = True
        while True:
            print(self.get_navigation())
            time.sleep(self.minute) # wait a minute
            t = 1 # time interval 1  minute
            self.x += self.speed/60 * sin(self.course) * t
            self.y += self.speed/60 * cos(self.course) * t

    def stop(self):
        """stop thread"""
        threading.Thread.join(self,timeout=1)

    def get_position(self):
        """atribute getter"""
        return(self.y, self.x)

    def get_latitude(self):
        """atribute getter"""
        return self.y/60   # minutes NB

    def get_longitude(self):
        """atribute getter"""
        return self.x/ (60 * cos(self.get_latitude()*pi/180)) # minutes OL

    def decode_gll(self, vggll:str) -> dict:
        """Decode GLL NMEA sentence into a dictionary."""
        fields = vggll.split(',')
        if len(fields) < 7:
            raise ValueError("Invalid GLL sentence")
        lat = float(fields[1][:2]) + float(fields[1][2:]) / 60.0
        if fields[2] == 'S':
            lat = -lat
        self.lat = lat
        lon = float(fields[3][:3]) + float(fields[3][3:]) / 60.0
        if fields[4] == 'W':
            lon = -lon
        self.lon = lon

        self.utc_time = fields[5]
        self.status = fields[6]

        return {
            'latitude': lat,
            'longitude': lon,
            'time_utc': self.utc_time,
            'status': self.status
        }

    def decode_vts(self, gpvtg:str) -> dict:
        """Decode VTG NMEA sentence into a dictionary."""
        fields = gpvtg.split(',')
        if len(fields) < 9:
            raise ValueError("Invalid VTG sentence")
        if fields[1] == '':
            self.course = None
            self.heading = None
            self.speed   = None
            speed_kmh = None
        else:
            self.course = float(fields[1])
            self.heading = float(fields[3])
            self.speed = float(fields[5])
            speed_kmh = float(fields[7])
        return {
            'true_track': self.course,
            'magnetic_track': self.heading,
            'speed_knots': self.speed,
            'speed_kmh': speed_kmh
        }

    def decode_zda(self, gpzda:str) -> dict:
        """Decode ZDA NMEA sentence into a dictionary."""
        fields = gpzda.split(',')
        if len(fields) < 5:
            raise ValueError("Invalid ZDA sentence")
        self.utc_time = fields[1]
        self.day = int(fields[2])
        self.month = int(fields[3])
        self.year = int(fields[4])
        return {
            'time_utc': self.utc_time,
            'day': self.day,
            'month': self.month,
            'year': self.year
        }

    def decode_hdt(self, gphdt:str) -> dict:
        """Decode HDT NMEA sentence into a dictionary."""
        fields = gphdt.split(',')
        if len(fields) < 2:
            raise ValueError("Invalid HDT sentence")
        heading = float(fields[1])
        return {'heading': heading}


    def decode_rmc(self, gprmc:str) -> dict:
        """Decode RMC NMEA sentence into a dictionary."""
        fields = gprmc.split(',')
        if len(fields) < 12:
            raise ValueError("Invalid RMC sentence")
        time_utc = fields[1]
        status = fields[2]
        lat = float(fields[3][:2]) + float(fields[3][2:]) / 60.0
        if fields[4] == 'S':
            lat = -lat

        lon = float(fields[5][:3]) + float(fields[5][3:]) / 60.0
        if fields[6] == 'W':
            lon = -lon

        speed_over_ground = float(fields[7])
        if speed_over_ground == '':
                speed_over_ground = None
        else:
            speed_over_ground = float(fields[7])
        if fields[8] == '':
            course_over_ground = None
        else:
            course_over_ground = float(fields[8])
        date = fields[9]

        return {
            'time_utc': time_utc,
            'status': status,
            'latitude': lat,
            'longitude': lon,
            'speed_over_ground': speed_over_ground,
            'course_over_ground': course_over_ground,
            'date': date
        }

    def gps_from_signalk(self, host ='localhost', port=10110):
        """Generator that yields GPS data from a SignalK server."""
        with socket(AF_INET, SOCK_STREAM) as s:
            s.connect((host, port))
            buffer = ""
            print('socket opened')
            while True:
                data = s.recv(4096).decode('utf-8')
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)

                    if line.startswith("$GRMC"):
                        self.navigation = self.decode_rmc(line)
                        yield self.navigation
                    elif line.startswith("$GPGLL"):
                        self.navigation = self.decode_gll(line)
                        yield self.navigation
                    elif line.startswith("$GPRMC"):
                        self.navigation = self.decode_rmc(line)
                        yield self.navigation
                    elif line.startswith("$GPVTG"):
                        self.navigation = self.decode_vts(line)
                        yield self.navigation
                    elif line.startswith("$GPZDA"):
                        self.navigation = self.decode_zda(line)
                        yield self.navigation
                    elif line.startswith("$GPHDT"):
                        self.navigation = self.decode_hdt(line)
                        yield self.navigation

if __name__ == '__main__':
    my_ship = Ship(244030153, 53.26379, 7.39738, 180, 1.0, '127.0.0.1', 10110)
    my_ship.start()
    print(my_ship.get_course(), my_ship.get_speed())
    while True:
        print(f'Lattitude: {my_ship.get_latitude():.3f}, longitude: {my_ship.get_longitude():.3f}')
        print(my_ship.get_navigation())
        time.sleep(30)
    my_ship.stop()

