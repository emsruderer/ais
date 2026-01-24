# Module Imports
import sys
import time as t
import datetime
from threading import Thread
import gc
from pyais.tracker import AISTrackEvent
import pyais
from pyais.stream import TCPConnection
from pyais.exceptions import UnknownMessageException
from pyais.filter import haversine
import mysql.connector
from cpa_tcpa import cpa_tcpa
from SQL_Statements import ADD_SHIP, UPDATE_SHIP, ADD_WAYPOINT, ADD_SHIP_24, UPDATE_SHIP_24, REPORT, ROMP_SPEED,SHIP_DATA



host = 'localhost'
port = 10110
jemgum_lat = 53.26417
jemgum_lon = 7.396137
# 53.2641733575126° , 7.396137714385986°
jemgum = (jemgum_lat,jemgum_lon)
# 53.269537800047864° , 7.396695613861085°
north_border = (53.27338,7.3967)
south_border = (53.25540, 7.394914627075195)

print(haversine(jemgum,north_border))
print(haversine(jemgum,south_border))

# Connect to MariaDB Platform
try :
    conn = mysql.connector.connect(
        user="nanno",
        password="11082004",
        host='localhost',
        port=3306,
        database="db_ais"
    )

except Exception as e:
    print(f"Error connecting to MariaDB Platform  {e}")
    sys.exit(1)

cur = conn.cursor()

print("Connected")
conn.autocommit = True
print(conn.autocommit)



tracker = pyais.AISTracker()
latest_tracks = None


#lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')

def handle_create(decoded_msg):
    """ called every time a new AISTrack is created """
    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
    data_ship = (decoded_msg.mmsi, decoded_msg.imo, decoded_msg.callsign, decoded_msg.shipname,decoded_msg.ship_type, decoded_msg.to_bow, decoded_msg.to_stern, decoded_msg.to_port, decoded_msg.to_starboard,  lt)
    print(data_ship)
    cur.execute(ADD_SHIP,data_ship)


def handle_update(track):
    """ called every time an AISTrack is updated """
    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
    # called every time an AISTrack is updated
    data_ship = ( track.mmsi, track.imo, track.callsign, track.shipname, track.ship_type, track.to_bow, track.to_stern, track.to_port, track.to_starboard, lt, track.mmsi)
    print( data_ship)
    print(track)
    #cur.execute(UPDATE_SHIP,data_ship)
    if in_range(track.lat,track.lon) :
        data_ship = (track.mmsi, track.speed, track.lat, track.lon, track.course, track.heading, lt )
        cur.execute(ADD_WAYPOINT,data_ship)

def handle_delete(track):
    """ called every time an AISTrack is deleted (pruned) """
    # called every time an AISTrack is deleted (pruned)
    print('delete', track.mmsi)

def in_range(lat,lon):
    """ check if ship is within range of jemgum """
    if (lat and lon):
        distance = haversine((jemgum_lat,jemgum_lon), (lat,lon))
        return distance <= 25.5
    else:
        return False

def romp_snelheid(mmsi):
    """ calculate romp snelheid """
    cur = conn.cursor()
    cur.execute(romp_speed,mmsi)
    el = cur.fetchone()
    cur.close()
    print(el)
    return el

def warning(mmsi):
    """ create warning """
    cur = conn.cursor()
    cur.execute(ship_data,[mmsi])
    for ship in cur:
        pass
    cur.close()
    try:
        mmsi = ship[0]
        time = ship[1]
        speed = ship[2]
        lat = ship[3]
        lon = ship[4]
        course = ship[5]
        heading = ship[6]
        name= ship[7]
        callsign = ship[8]
        typ = ship[9]
        s = F"{mmsi:n} {time} {speed:5.1f} {lat:8.4f} {lon:8.4f} {course:6.1f} {heading:6.1f} {name:24} {callsign:8} {ship_type(typ)}"
        print(s)
        #call_ship(mmsi,name,callsign)
    except Exception as e:
        print(e)




with pyais.AISTracker() as tracker:
    tracker.register_callback(AISTrackEvent.CREATED, handle_create)
    tracker.register_callback(AISTrackEvent.UPDATED, handle_update)
    tracker.register_callback(AISTrackEvent.DELETED, handle_delete)


def do_track():
    """
    Docstring for do_track
    """
    _cpa_tcpa = dict()
    cur = conn.cursor()
    global latest_tracks
    for msg in TCPConnection(host=host, port=port):
        try:
            decoded_msg = msg.decode()
            if (decoded_msg.msg_type in [1,2,3,18]) :
                if in_range(decoded_msg.lat,decoded_msg.lon) and decoded_msg.speed > 0.5 and decoded_msg.speed < 102.3:
                    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
                    data_ship = (decoded_msg.mmsi, decoded_msg.speed, decoded_msg.lat, decoded_msg.lon, decoded_msg.course, decoded_msg.heading, lt )
                    cur.execute(ADD_WAYPOINT,data_ship)
                    conn.commit()
                    _cpa_tcpa[decoded_msg.mmsi]= cpa_tcpa(decoded_msg.speed, decoded_msg.lat, decoded_msg.lon, decoded_msg.course, 244030153, 0, jemgum_lat,jemgum_lon, 180, 0)
            elif (decoded_msg.msg_type == 5) :
                    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
                    data_ship = (decoded_msg.mmsi, decoded_msg.imo, decoded_msg.callsign, decoded_msg.shipname,decoded_msg.ship_type, decoded_msg.to_bow, decoded_msg.to_stern, decoded_msg.to_port, decoded_msg.to_starboard,  lt)
                    cur.execute(ADD_SHIP,data_ship)
                    conn.commit()
            elif (decoded_msg.msg_type == 24) :
                lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
                if (decoded_msg.partno == 0):
                    data_ship = (decoded_msg.mmsi, decoded_msg.shipname, lt)
                    cur.execute(ADD_SHIP_24,data_ship)
                    conn.commit()
                elif (decoded_msg.partno == 1):
                    data_ship = (decoded_msg.callsign, decoded_msg.ship_type, decoded_msg.to_bow, decoded_msg.to_stern, decoded_msg.to_port, decoded_msg.to_starboard, decoded_msg.mmsi)
                    cur.execute(UPDATE_SHIP_24,data_ship)
                    conn.commit()
            tracker.update(decoded_msg)
            latest_tracks = tracker.n_latest_tracks(10)
        except UnknownMessageException as ex:
            print(ex)


t1 = Thread(target=do_track,)
t1.start()

def ship_type(n):
    """ return ship type """
    return str(n)+" unavailable"

def show():
    """ show report every minute """
    #gc.set_debug(gc.DEBUG_LEAK)
    while True:
        t.sleep(60)
        cur = conn.cursor()
        cur.execute(REPORT)
        print("_________________________________________________________________________________________________________________________")
        print("mmsi            time            speed  lat      lon    course heading name                   callsign type")
        print("_________________________________________________________________________________________________________________________")
        for (ship) in cur:
            #for i in range(10):
            #   print(ship[i],end=' ')
            try:
                mmsi = ship[0]
                time = ship[1]
                speed = ship[2]
                lat = ship[3]
                lon = ship[4]
                course = ship[5]
                heading = ship[6]
                name= ship[7]
                callsign = ship[8]
                typ = ship[9]
                s = F"{mmsi:n} {time} {speed:5.1f} {lat:8.4f} {lon:8.4f} {course:6.1f} {heading:6.1f} {name:24} {callsign:8} {ship_type(typ)}"
                print(s)
                #if  speed > 11:
                #    call_ship(mmsi,name,callsign)
            except Exception as ex:
                print(ex)
        t.sleep(10)
        cur.close()
        print("_________________________________________________________________________________________________________________________")
        n = gc.collect()
        print(n)


t2 = Thread(target= show)
t2.start()
t1.join()
t2.join()
cur.close()
conn.close()
print(gc.garbage)
