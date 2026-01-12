""" ais NMEA 0183 stream from SignalK port 10110 """
import sys
from multiprocessing import Queue, Process
from pyais.stream import TCPConnection
from pyais.filter import FilterChain,MessageTypeFilter,NoneFilter
from pyais.tracker import AISTrackEvent
from cpa_tcpa import cpa_tcpa
from cpa_tracker import CPATracker
from ships import Ship
from warn import do_warn

HOST = "localhost"
PORT = 10110
VERBOSE = False
MAX_MESSAGES = 100
MINIMUM_CPA = 1.0 # nautical miles
MINIMUM_TCPA = 15   # minutes
MINIMUM_DISTANCE = 10 # nautical miles

"""Define the filter chain with various criteria """
chain = FilterChain([
    NoneFilter('lon', 'lat', 'mmsi'),
    MessageTypeFilter(1, 2, 3, 5, 18, 19, 24),
    ])

def pretty_print(tracks):
    """Pretty print a list of tracks to stdout."""
    headers = ['mmsi', 'callsign', 'shipname', 'lat', 'lon', 'cpa', 'tcpa', 'distance', 'bearing']
    rows = [[getattr(t, a) or 'N.A.' for a in headers] for t in tracks]
    row_format = "{:>20}" * (len(headers) + 1)
    sys.stdout.write(row_format.format(" ", *headers) + '\n')

    for i, row in enumerate(rows, start=1):
        sys.stdout.write(row_format.format(i, *row) +'\n')

def live_print(tracks):
    """Live print a list of tracks to stdout."""
    for _ in range(len(tracks) + 1):
        sys.stdout.write("\x1b[1A\x1b[2K")  # move up cursor and delete whole line
    pretty_print(tracks)


print('\n' * 10)

def danger(cpa,minimum_cpa=MINIMUM_CPA,minimum_tcpa=MINIMUM_TCPA,minimum_distance=MINIMUM_DISTANCE):
    """Determine if a CPA is dangerous."""
     # nautical miles
    if cpa['tcpa'] is not None and cpa['tcpa'] < minimum_tcpa and cpa['tcpa'] > 0\
         and cpa['cpa'] < minimum_cpa and cpa['distance'] < minimum_distance:
        return True
    return False

def handle_create(track):
    """called every time an CPATrack is created"""
    #print('created:', track)


def handle_update(track):
    """called every time an CPATrack is updated"""
    print('updated',track)


def handle_delete(track):
    """called every time an CPATrack is deleted (pruned)"""
    #print('deleted',track)

def do_track(que, known_ship = None):
    """tracking function"""
    with CPATracker() as tracker:
        tracker.register_callback(AISTrackEvent.CREATED, handle_create)
        tracker.register_callback(AISTrackEvent.UPDATED, handle_update)
        tracker.register_callback(AISTrackEvent.DELETED, handle_delete)
        with TCPConnection('localhost', 10110) as ais_stream:
            for msg in ais_stream:
                decoded = msg.decode()
                cpa_res = { "cpa": None, "tcpa": None, "distance": None, "bearing": None, "approaching_speed": None }
                if decoded.msg_type in [1,2,3,18]:
                    cpa_res = cpa_tcpa( known_ship.get_mmsi(),known_ship.get_latitude(),
                                        known_ship.get_longitude(),
                                        known_ship.get_course(), known_ship.get_speed(),
                                        decoded.mmsi,
                                        decoded.lat,
                                        decoded.lon,
                                        decoded.course or 0.0,
                                        decoded.speed or 0.0)
                    #print_cpa(decoded.mmsi, cpa_res)
                    tracker.update(decoded, cpa_res)
                    if danger(cpa_res):
                        que.put( tracker.get_track(decoded.mmsi)   )
                        print("Dangerous CPA detected for MMSI ", decoded.mmsi)
                elif decoded.msg_type in [5,18,19,24]:
                    tracker.update(decoded, cpa_res)
                    #print("Updated non position message for MMSI ", decoded )
                latest_tracks = tracker.n_latest_tracks(10)
                #print_tracks(latest_tracks)
                #live_print(latest_tracks)


if __name__ == '__main__':
    VERBOSE = True
    print(VERBOSE)
    my_ship = Ship(244030153, 53.26379, 7.39738,0,5.0)
    my_ship.start()
    warn_que = Queue(MAX_MESSAGES)
    p1 = Process(target=do_track, args=(warn_que,my_ship,))
    p1.start()
    p3 = Process(target=do_warn, args=(warn_que, my_ship,))
    p3.start()
    p1.join()
    p3.join()
    warn_que.close()
    my_ship.stop()
