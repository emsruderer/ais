"""
Ship class for virtual ships simulationS
"""

import time
from math import sin,cos, radians, degrees
import threading
from socket import socket, AF_INET, SOCK_STREAM

class Ship(threading.Thread):
    """Virtual sailing ship"""
    def __init__(self, mmsi, lat, lon, course, speed, host='localhost', port=10110 ):
        threading.Thread.__init__(self)
        self.mmsi = mmsi
        self.host = host
        self.port = port
        self.lat = lat
        self.lon = lon
        self.y = lat*60
        self.x = lon*60 * cos(radians(lat))  # nautical miles OL
        self.cog = radians(course) # rad
        self.heading = course # heading in degrees
        self.sog = speed # knots
        self.minute = 60 #60
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
        self.navigation = {'lat': self.lat, 'lon' : self.lon, 'cog': self.get_cog(), 'sog': self.sog}
        return self.navigation

    def _get_latitude(self):
        """atribute getter"""
        return self.y   # nautical miles NB

    def _get_longitude(self):
        """atribute getter"""
        return self.x # nautical miles OL

    def get_cog(self):
        """atribute getter"""
        return degrees(self.cog) # in degrees

    def set_cog(self,course):
        """atribute setter"""
        self.cog = radians(course)

    def get_sog(self):
        """atribute getter"""
        return self.cog

    def run(self):
        """thread runner"""
        super().run()
        self.deadreckoning = False
        try:
            for gps in self.gps_from_signalk(host ='localhost', port=10110):
                self.navigation = gps
                print(self.get_navigation())
        except Exception as e:
            print(f'GPS stream error: {e}')
            print('Switching to dead reckoning mode')

        self.deadreckoning = True
        while True:
            print(self.get_navigation())
            time.sleep(self.minute) # wait a minute
            t = self.minute / 60 # time interval 1  minute
            dx = self.sog/60 * sin(self.cog) * t
            dy = self.sog/60 * cos(self.cog) * t
            self.x += dx
            self.y += dy
            self.lon += dx/60
            self.lat += dy/60

    def stop(self):
        """stop thread"""
        threading.Thread.join(self,timeout=1)

    def get_position(self):
        """atribute getter"""
        return (self.lat, self.lon)

    def get_latitude(self):
        """atribute getter"""
        return self.lat  # minutes NB

    def get_longitude(self):
        """atribute getter"""
        return self.lon

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
            'latitude': self.lat,
            'longitude': self.lon,
            'time_utc': self.utc_time,
            'status': self.status
        }

    def decode_vtg(self, gpvtg:str) -> dict:
        """Decode VTG NMEA sentence into a dictionary."""
        fields = gpvtg.split(',')
        if len(fields) < 9:
            raise ValueError("Invalid VTG sentence")
        if fields[1] == '':
            course = None
            heading = None
            speed   = None
            speed_kmh = None
        else:
            self.cog = float(fields[1])
            self.heading = float(fields[3])
            self.sog = float(fields[5])
            speed_kmh = float(fields[7])
        return {
            'cog': self.cog,
            'magnetic_track': self.heading,
            'sog': self.sog,
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
        self.lat = lat
        lon = float(fields[5][:3]) + float(fields[5][3:]) / 60.0
        if fields[6] == 'W':
            lon = -lon
        self.lon = lon

        speed_over_ground = float(fields[7])
        if speed_over_ground == '':
                speed_over_ground = None
        else:
            self.sog = float(fields[7])
        if fields[8] == '':
            course_over_ground = None
        else:
            self.cog = radians(float(fields[8]))
        date = fields[9]

        return {
            'time_utc': time_utc,
            'status': status,
            'latitude': self.lat,
            'longitude': self.lon,
            'sog': self.sog,
            'cog': self.cog,
            'date': date
        }

    def gps_from_signalk(self, host ='localhost', port=10110):
        """Generator that yields GPS data from a SignalK server."""
        fail_counter = 0
        with socket(AF_INET, SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((host, port))
            buffer = ""
            print('socket opened')
            while True:
                try:
                    data = s.recv(4096,).decode('utf-8')
                    if not data:
                        fail_counter += 1
                        if fail_counter > 5:
                            raise RuntimeWarning('No data from GPS')
                        break
                    buffer += data
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        if line.startswith("$GRMC"):
                            self.navigation = self.decode_rmc(line)
                            yield(self.navigation)
                        elif line.startswith("$GPGLL"):
                            self.navigation = self.decode_gll(line)
                            yield(self.navigation)
                        elif line.startswith("$GPVTG"):
                            self.navigation = self.decode_vts(line)
                            yield(self.navigation)
                        elif line.startswith("$GPZDA"):
                            self.navigation = self.decode_zda(line)
                            yield (self.navigation)
                        elif line.startswith("$GPHDT"):
                            self.navigation = self.decode_hdt(line)
                            yield (self.navigation)
                except Exception as ex:
                    print(ex,line)
                    if RuntimeWarning:
                        raise RuntimeWarning from RuntimeWarning
                    
if __name__ == '__main__':
    my_ship = Ship(244030153, 53.26379, 7.39738, 180, 1.0, '127.0.0.1', 10110)
    my_ship.start()
    print(my_ship.get_cog(), my_ship.get_sog())
    while True:
        print(f'Lattitude: {my_ship.get_latitude():.3f}, longitude: {my_ship.get_longitude():.3f}')
        print(my_ship.get_navigation())
        time.sleep(30)
    my_ship.stop()

