"""
Ship class for virtual ships simulationS
"""

import time
from math import sin,cos,pi
import threading

class Ship(threading.Thread):
    """Virtual sailing ship"""
    def __init__(self, mmsi, lat, lon, course,speed):
        threading.Thread.__init__(self)
        self.mmsi = mmsi
        self.y = lat*60
        self.x = lon*60 * cos(lat*pi/180)  # nautical miles OL
        self.course = course*pi/180 # course in rad
        self.speed = speed/60  # nm per min
        self.minute = 60

    def get_mmsi(self):
        """atribute getter"""
        return str(self.mmsi)

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
        while True:
            time.sleep(self.minute) # wait a minute
            t = 1 # time interval 1  minute
            self.x += self.speed * sin(self.course) * t
            self.y += self.speed * cos(self.course) * t
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

if __name__ == '__main__':
    my_ship = Ship(244030153, 53.26379, 7.39738, 180, 25.0)
    my_ship.start()
    print(my_ship.get_course(), my_ship.get_speed())
    for t0 in range(10):
        for t1 in range(4):
            print(f'Lattitude: {my_ship.get_latitude():.3f}, longitude: {my_ship.get_longitude():.3f}')
            time.sleep(60)
        my_ship.set_course((my_ship.get_course()+90)%360)
        print(f'new course {my_ship.get_course():.2f}')
        time.sleep(60)
        