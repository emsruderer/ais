""" multi_process_ais """

from multiprocessing import Process, Queue
from pyais.filter import haversine
from ais_stream import do_track
from ships import Ship
from warn import do_warn


VERBOSE = True
HOST = "localhost"
PORT = 10110
MAX_MESSAGES = 100

JEMGUM_LAT = 53.26379
JEMGUM_LON = 7.39738
JOHANNA = 244030153
LOOK_AROUND_RADIUS = 7.0  # in nautical miles

def in_range(lat,lon, lat2=JEMGUM_LAT, lon2=JEMGUM_LON):
    """range of interest"""
    return haversine((lat2, lon2),  (lat,lon)) < LOOK_AROUND_RADIUS


def show_msg(msg):
    """pretty print """
    for k,v in msg.items():
        print(k,v)
    print('_' * 20)


class Decoder:
    def __init__(self, q, wq, ower_ship):
        self.q = q
        self.warn_que = wq
        self.ship = ower_ship

    def do_decode(self):
        """Decode Process"""

        known_ships_a = dict()
        known_ships_b = dict()

        while True:
            raw = self.q.get()
            msg = raw.decode()
            ais_content = msg.asdict()
            if msg.msg_type in [19,24]:
                if msg.partno==0:
                    known_ships_a[ais_content['mmsi']] = ais_content
                elif msg.partno==1 :
                    known_ships_b[ais_content['mmsi']] = ais_content
                show_msg(ais_content)
            elif msg.msg_type in [1,2,3,18]:
                if in_range(ais_content['lat'],ais_content['lon'], self.ship.get_latitude(), self.ship.get_longitude()):
                    if ais_content['mmsi'] in known_ships_a:
                        show_msg(ais_content)
                    if ais_content['mmsi'] in known_ships_b:
                        show_msg(known_ships_b[ais_content['mmsi']])
                    show_msg(ais_content)
                    self.warn_que.put(raw, False,0)


    def run(self):
        """run subprocess"""
        self.do_decode()


if __name__ == '__main__':
    my_ship = Ship(JOHANNA,JEMGUM_LAT,JEMGUM_LON,287,5.0)
    my_ship.start()
    que = Queue(MAX_MESSAGES)
    warn_que = Queue(MAX_MESSAGES)
    decoder = Decoder(que, warn_que, my_ship)
    p1 = Process(target=do_track, args=(que,))
    p1.start()
    p2 = Process(target=decoder.do_decode, args=())
    p2.start()
    p3 = Process(target=do_warn, args=(warn_que, my_ship,))
    p3.start()
    p1.join()
    p2.join()
    p3.join()
    que.close()
    warn_que.close()

