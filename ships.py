"""
Ship class for virtual ships simulations
Be careful not meant for sailing just for simulation and testing
Real valid shipsdata should be used
"""

import time
from math import sin, cos, atan2, radians, degrees, sqrt
import threading
from socket import socket, AF_INET, SOCK_STREAM

class Ship(threading.Thread):
<<<<<<< HEAD
    """ Virtual sailing ship for testing purposes
    parameters:
        shipsdata : mmsi, initial position lat and lon, course over ground, speed over ground
        gps host and port
    """
    def __init__(self, mmsi, lat, lon, cog, sog, host='localhost', port=10110 ):
=======
    """Virtual sailing ship"""
    def __init__(self, mmsi, lat, lon, course,speed, host='localhost', port=10110 ):
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
        threading.Thread.__init__(self)
        self.mmsi = mmsi
        self.host = host
        self.port = port
        self.lat = lat
        self.lon = lon
<<<<<<< HEAD
        self.cog = radians(cog) # cog in rad
        self.heading = cog # heading in degrees
        self.sog = sog # knots
        self.y = lat*60
        self.x = lon*60
        self.dy = self.sog * cos(self.cog)  # knots to North
        self.dx = self.sog * sin(self.cog)  # knots to East
        self.minute = 60 # seconds
        self.deadreckoning = True
        self.mode = 'N' # data not valid  (values A: autonomous, D; differential, E: estimated)
=======
        self.y = lat*60
        self.x = lon*60 * cos(lat*pi/180)  # nautical miles OL
        self.course = course*pi/180 # course in rad
        self.heading = course # heading in degrees
        self.speed = speed # knots
        self.minute = 1 #60
        self.deadreckoning = True
        self.navigation = {}
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
        self.utc_time = None
        self.date = None
        self.day = None
        self.month = None
        self.year = None
        self.status = None
<<<<<<< HEAD
        self.variation = 3.3
        self.navigation = {}
        print(self.dy,self.dx)

=======
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e

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

    def get_cog(self):
        """atribute getter"""
        return degrees(self.cog) # in degrees

    def set_cog(self,cog):
        """atribute setter"""
        self.cog = radians(cog)
        self.dx = self.sog * sin(self.cog)
        self.dy = self.sog * cos(self.cog)

    def get_sog(self):
        """atribute getter"""
        return self.sog

    def run(self):
        """thread runner"""
        super().run()
        self.deadreckoning = False
<<<<<<< HEAD
        print("ship sailing")
        try:
            for gps in self.gps_from_signalk(host ='localhost', port=10110):
                pass

        except RuntimeWarning as e:
=======
        try:
            for gps in self.gps_from_signalk(host ='localhost', port=10110):
                self.navigation = gps
                #print(self.get_navigation())

        except RuntimeError as e:
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
            print(f'GPS stream error: {e}')
            print('Switching to dead reckoning mode')

        self.deadreckoning = True
<<<<<<< HEAD
        self.cog = (degrees(atan2(self.dx,self.dy)) + 360)%360
        self.sog = sqrt(self.dy**2+self.dx**2)
        print(self.cog, self.sog)
=======
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
        while True:
            print(self.get_navigation())
            time.sleep(self.minute) # wait a minute
<<<<<<< HEAD
            t = self.minute # time interval 1  minute
            self.x += self.dx/60 * t  # knots a minute eastward
            self.y += self.dy/60 * t  # knots a minute nortward
            self.lat = self.y/60   # miles north of equator / 60  = deg N
            self.lon = self.x/60   # miles east of greenwich / 60 = deg E
=======
            t = 1 # time interval 1  minute
            self.x += self.speed/60 * sin(self.course) * t
            self.y += self.speed/60 * cos(self.course) * t
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e

    def stop(self):
        """stop thread"""
        threading.Thread.join(self,timeout=1)

    def get_position(self):
        """atribute getter"""
        return(self.y, self.x)

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
<<<<<<< HEAD
        self.lat = float(fields[1][:2]) + float(fields[1][2:]) / 60.0
        if fields[2] == 'S':
            self.lat = -self.lat
        self.lon = float(fields[3][:3]) + float(fields[3][3:]) / 60.0
        if fields[4] == 'W':
            self.lon = -self.lon
=======
        lat = float(fields[1][:2]) + float(fields[1][2:]) / 60.0
        if fields[2] == 'S':
            lat = -lat
        self.lat = lat
        lon = float(fields[3][:3]) + float(fields[3][3:]) / 60.0
        if fields[4] == 'W':
            lon = -lon
        self.lon = lon

>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
        self.utc_time = fields[5]
        self.status = fields[6]

        return {
<<<<<<< HEAD
            'latitude': self.lat,
            'longitude': self.lon,
=======
            'latitude': lat,
            'longitude': lon,
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
            'time_utc': self.utc_time,
            'status': self.status
        }

<<<<<<< HEAD
    def decode_vtg(self, gpvtg:str) -> dict:
=======
    def decode_vts(self, gpvtg:str) -> dict:
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
        """Decode VTG NMEA sentence into a dictionary."""
        fields = gpvtg.split(',')
        if len(fields) < 9:
            raise ValueError("Invalid VTG sentence")
<<<<<<< HEAD
        if fields[1] == '' or fields[9] =='N':
            self.cog = None
            self.heading = None
            self.sog   = None
            self.mode ='N'
        else:
            self.cog = radians(float(fields[1]))
            self.heading = float(fields[3])
            self.sog = float(fields[5])
            self.mode = fields[9]
        return {
            'cog': self.cog,
            'heading': self.heading,
            'sog': self.sog,
            'mode': self.mode
=======
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
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
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
<<<<<<< HEAD
        self.heading = float(fields[1])
        return {'heading': self.heading}
=======
        heading = float(fields[1])
        return {'heading': heading}
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e


    def decode_rmc(self, gprmc:str) -> dict:
        """Decode RMC NMEA sentence into a dictionary."""
        fields = gprmc.split(',')
        if len(fields) < 12:
            raise ValueError("Invalid RMC sentence")
<<<<<<< HEAD
        self.utc_time = fields[1]
        self.status = fields[2] # Active or Void
        self.lat = float(fields[3][:2]) + float(fields[3][2:]) / 60.0
        if fields[4] == 'S':
            self.lat = -self.lat

        self.lon = float(fields[5][:3]) + float(fields[5][3:]) / 60.0
        if fields[6] == 'W':
            self.lon = -self.lon

        self.sog = float(fields[7])
        if self.sog == '':
                self.sog = 0.0
        if fields[8] == '':
            self.cog = None
        else:
            self.cog = radians(float(fields[8]))
        self.date = fields[9]
        self.variation = fields[8]

        return {
            'time_utc': self.utc_time,
            'status': self.status,
            'latitude': self.lat,
            'longitude': self.lon,
            'sog': self.sog,
            'cog': self.cog,
            'date': self.date
=======
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
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
        }

    def gps_from_signalk(self, host ='localhost', port=10110):
        """Generator that yields GPS data from a SignalK server."""
        with socket(AF_INET, SOCK_STREAM) as s:
            s.connect((host, port))
            buffer = ""
            print('socket opened')
            while True:
                try:
                    data = s.recv(4096).decode('utf-8')
                    if not data:
                        break
                    buffer += data
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
<<<<<<< HEAD
                        if line.startswith("$GPRMC"):
                            self.navigation = self.decode_rmc(line)
                            yield(self.navigation)
                        elif line.startswith("$GPGLL"):
                            self.navigation = self.decode_gll(line)
                            yield(self.navigation)
                        elif line.startswith("$GPVTG"):
                            self.navigation = self.decode_vtg(line)
                            if self.navigation['mode'] == 'N':
                                raise RuntimeWarning('no valid ailing data')
                            yield(self.navigation)
                        elif line.startswith("$GPZDA"):
                            self.navigation = self.decode_zda(line)
                            yield(self.navigation)
                        elif line.startswith("$GPHDT"):
                            self.navigation = self.decode_hdt(line)
                            yield(self.navigation)
                        #print(self.navigation)
                except ConnectionRefusedError as ex:
                    print(ex,line)
                    raise RuntimeWarning(ex,line) from ex

=======

                        if line.startswith("$GRMC"):
                            self.navigation = self.decode_rmc(line)
                            yield #self.navigation
                        elif line.startswith("$GPGLL"):
                            self.navigation = self.decode_gll(line)
                            yield #self.navigation
                        elif line.startswith("$GPVTG"):
                            self.navigation = self.decode_vts(line)
                            yield #self.navigation
                        elif line.startswith("$GPZDA"):
                            self.navigation = self.decode_zda(line)
                            yield #self.navigation
                        elif line.startswith("$GPHDT"):
                            self.navigation = self.decode_hdt(line)
                            yield #self.navigation
                except Exception as ex:
                    print(ex,line)
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e

if __name__ == '__main__':
    my_ship = Ship(244030153, 53.26379, 7.39738, 180, 1.0, '127.0.0.1', 10110)
    my_ship.start()
<<<<<<< HEAD
    print(f'Lattitude: {my_ship.get_latitude():.3f}, longitude: {my_ship.get_longitude():.3f}  dy: {my_ship.dy} dx: {my_ship.dx}')
    while True:
        time.sleep(60)
        print(f'Lattitude: {my_ship.get_latitude():.3f}, longitude: {my_ship.get_longitude():.3f}  dy: {my_ship.dy} dx: {my_ship.dx}')
        my_ship.set_cog(my_ship.get_cog() + 90)

=======
    print(my_ship.get_course(), my_ship.get_speed())
    while True:
        print(f'Lattitude: {my_ship.get_latitude():.3f}, longitude: {my_ship.get_longitude():.3f}')
        print(my_ship.get_navigation())
        time.sleep(30)
>>>>>>> bd562294c660f4f9ea56ce512cd4b0bee6cc438e
    my_ship.stop()

