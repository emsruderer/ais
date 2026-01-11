from pyais.stream import TCPConnection
from pyais import decode
from pyais.filter import haversine
import threading
import time
from ships import Ship
from threading import Lock
from math import pi, cos, sin

VERBOSE = True
VERBOSE = False

baton = Lock()

def cpa_tcpa(mmsi1, lat1, lon1, course1, speed1,  mmsi2, lat2, lon2, course2, speed2):
    try:
        DVx = speed1*sin(course1*pi/180) - speed2*sin(course2*pi/180) 
        DVy = speed1*cos(course1*pi/180) - speed2*cos(course2*pi/180) 

        Dx = (lon1 - lon2)*60*sin(((lat1+latrom pyais.filter ifmport haversine2)/2)*pi/180)
        Dy = (lat1 - lat2)*60

        tcpa = -(Dy*DVy+Dx*DVx)/(DVy**2 + DVx**2)
        cpa = abs(Dx*DVy - Dy*DVx) / pow(DVy**2 + DVx**2, 0.5)

        #print(f"Delta lon {Dx:.4}, delta Vx {DVx:.4}, Delta lat {Dy:.4}, delta Vy {DVy:.4}")
        
        return { "cpa": cpa, "tcpa" : tcpa, "mmsi" : mmsi2 }
    except Exception as ex:
        print(ex, mmsi1 )
        return { "cpa": 0, "tcpa" : 0, "mmsi" : mmsi2 }

class Receiver(threading.Thread):
    def __init__(self, my_ship, host='localhost', port = 10110):
        threading.Thread.__init__(self)
        self.my_ship = my_ship
        self.host = host
        self.port = port

    known_shipsA = dict()
    known_shipsB = dict()
    ships = dict()

    jemgum_lat = 53.26379
    jemgum_lon = 7.39738

    def in_range(self, lat,lon, minimum):
        distance = haversine((self.jemgum_lat,self.jemgum_lon), (lat,lon))
        if VERBOSE: print(distance < minimum)
        return distance <= minimum
    
    def get_ships(self):
        return self.ships
    
    def run(self):
        for msg in TCPConnection(self.host, self.port):
            #print(msg.type)
            ais_content = msg.decode()
            msg_dict = ais_content.asdict()
            if ais_content.msg_type in [19,24]:
                #print('*' * 80)
                if msg.tag_block:
                    # decode & print the tag block if it is available
                    msg.tag_block.asdict()   
                    # print(msg.tag_block.asdict())
                    #print(ais_content)
                if ais_content.partno==0 :
                    self.known_shipsA[ais_content.mmsi] = msg_dict
                elif ais_content.partno==1 :
                    self.known_shipsB[ais_content.mmsi] = msg_dict
                    #print(known_ships)
            elif ais_content.msg_type in [1,2,3,18]:
                if self.in_range(ais_content.lat,ais_content.lon, 15.0) and ais_content.speed > 0.0 :
                    baton.acquire()
                    if VERBOSE and msg_dict['mmsi'] == '244030153':
                        print('Johanna send msg')
                    self.ships[msg_dict['mmsi']] = cpa_tcpa(msg_dict['mmsi'], msg_dict['lat'],msg_dict['lon'],msg_dict['course'],msg_dict['speed'],self.my_ship.get_mmsi(),self.my_ship.get_latitude(),self.my_ship.get_longitude(),self.my_ship.get_course(), self.my_ship.get_speed())
                    baton.release()
                    if msg.tag_block:
                        # decode & print the tag block if it is available
                        msg.tag_block.init()
                        print(msg.tag_block.asdict())
                        print(ais_content)
                    if ais_content.mmsi in self.known_shipsA:
                        print(self.known_shipsA[ais_content.mmsi])
                    if ais_content.mmsi in self.known_shipsB:
                        print(self.known_shipsB[ais_content.mmsi])
                    

if __name__ == '__main__':
    jemgum_lat = 53.26417
    jemgum_lon = 7.396137
    johanna = 244030153
    t0 = Ship(johanna,jemgum_lat,jemgum_lon,287,5.0)
    t0.start()
    t1 = Receiver(t0)
    t1.start()
    while True:
        time.sleep(10)
        baton.acquire()
        ships = t1.get_ships()
        for ships, data in ships.items():
            #for k,v in data.items():
            if data["tcpa"] < 0.0:
                pass
                if VERBOSE: print(f"The closest point of boat {ships}  to {data["mmsi"]} is passed")
            else:
                print(ships)
                print(f"The closest point of boat {ships} to {data["mmsi"]} is : {data["cpa"]} Nm in {data["tcpa"]} hr.")
        baton.release()
            
                     

    