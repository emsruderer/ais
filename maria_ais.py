# Module Imports
import sys
import pyais
from pyais.stream import TCPConnection
from pyais.tracker import AISTrackEvent
from pyais.exceptions import UnknownMessageException
import time as t
import datetime
from threading import Thread
from pyais.filter import haversine
import gc
import mysql.connector
from cpa_tcpa import cpa_tcpa
#from speech import call_ship
#from pyais import decode

#flatpak run io.dbeaver.DBeaverCommunity

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
        user="user",
        password="password
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
# SQL Statements

create_ships_table = """
    CREATE TABLE IF NOT EXISTS Ships (
        mmsi  INT(10) UNIQUE NOT NULL,
        imo  CHAR(10),
        callsign  CHAR(8),
        name  VARCHAR(20),
        type  TINYINT(3),
        to_bow   SMALLINT(3),
        to_stern   SMALLINT(3),
        to_port    SMALLINT(3),
        to_starboard   SMALLINT(3),
        last_updated  TIMESTAMP(6),
        ais_version  CHAR(4),
        ais_type  CHAR(2),
        status  VARCHAR(40),
        PRIMARY KEY (mmsi)
    );
"""

create_track_table = """
    CREATE TABLE IF NOT EXISTS Tracks (
        mmsi  INT(10),
        speed  FLOAT(4,1),
        lat  FLOAT(10,6),
        lon  FLOAT(10,6),
        course   FLOAT(4,1),
        heading  FLOAT(4,1),
        repeats  INT,
        time  TIMESTAMP,

        PRIMARY KEY (mmsi,lon,lat)
    );
"""

create_cpa_table = """
    CREATE TABLE IF NOT EXISTS Cpa (
        mmsi  INT(10),
        speed  FLOAT(4,1),
        lat  FLOAT(10,6),
        lon  FLOAT(10,6),
        course   FLOAT(4,1),
        heading  FLOAT(4,1),
        cpa FLOAT(10,6),
        tcpa FLOAT(10,6),
        time  TIMESTAMP,

        PRIMARY KEY (mmsi,lon,lat)
    );
"""

add_cpa = ("""INSERT IGNORE INTO Cpa (mmsi,speed,lat,lon,course,heading,cpa,tcpa,last_updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """)

add_ship = ("""INSERT IGNORE INTO Ships (mmsi,imo,callsign,name,type,to_bow,to_stern,to_port,to_starboard, last_updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """)

add_ship_24 = ("""INSERT IGNORE INTO Ships (mmsi, name, last_updated) VALUES (%s,%s,%s) """)

update_cpa = ("""UPDATE IGNORE INTO Cpa (mmsi,speed,lat,lon,course,heading,cpa,tcpa,last_updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """)

update_ship = ("UPDATE Ships " "SET imo=%s, callsign=%s, name=%s, type=%s, to_bow = %s, to_stern =%s, to_port =%s, to_starboard=%s,last_updated=%s WHERE mmsi = %s")

update_ship_24 = ("UPDATE IGNORE Ships " "SET callsign=%s, type=%s, to_bow = %s, to_stern =%s, to_port =%s, to_starboard=%s WHERE mmsi = %s")

add_waypoint = ("INSERT IGNORE INTO Tracks" "(mmsi,speed,lat,lon,course,heading,time)" "VALUES (%s,%s,%s,%s,%s,%s, %s);")

report = ("SELECT Tracks.mmsi, Tracks.time, MAX(Tracks.speed), Tracks.lat, Tracks.lon, Tracks.course, Tracks.heading, Ships.name, Ships.callsign, Ships.type FROM Tracks LEFT JOIN Ships ON Tracks.mmsi = Ships.mmsi GROUP BY Tracks.mmsi ORDER BY Tracks.time ;")

ship_data = ("SELECT Tracks.mmsi, Tracks.time, MAX(Tracks.speed), Tracks.lat, Tracks.lon, Tracks.course, Tracks.heading, Ships.name, Ships.callsign, Ships.type FROM Tracks LEFT JOIN Ships ON Tracks.mmsi = Ships.mmsi WHERE Tracks.mmsi = %s ;")

romp_speed = ("SELECT SQRT(to_bow + to_stern)*2.42 as rump_speed FROM Ships WHERE mmsi = %s")

#lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
cur.execute(create_ships_table)
cur.execute(create_track_table)
cur.execute(create_cpa_table)

def handle_create(decoded_msg):
    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
    data_ship = (decoded_msg.mmsi, decoded_msg.imo, decoded_msg.callsign, decoded_msg.shipname,decoded_msg.ship_type, decoded_msg.to_bow, decoded_msg.to_stern, decoded_msg.to_port, decoded_msg.to_starboard,  lt)
    print(data_ship)
    cur.execute(add_ship,data_ship)


def handle_update(track):
    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
    # called every time an AISTrack is updated
    data_ship = (track.imo, track.callsign, track.shipname, track.ship_type, track.to_bow, track.to_stern, track.to_port, track.to_starboard, lt, track.mmsi)
    #print( data_ship)
    #print(track)
    cur.execute(update_ship,data_ship)
    if in_range(track.lat,track.lon) :
        data_ship = (track.mmsi, track.speed, track.lat, track.lon, track.course, track.heading, lt )
        cur.execute(add_waypoint,data_ship)

def handle_delete(track):
    # called every time an AISTrack is deleted (pruned)
    print('delete', track.mmsi)

tracker = pyais.AISTracker()
latest_tracks = None

def in_range(lat,lon):
    if (lat and lon):
        distance = haversine((jemgum_lat,jemgum_lon), (lat,lon))
        return distance <= 25.5
    else:
        return False

def romp_snelheid(mmsi):
    cur = conn.cursor()
    cur.execute(romp_speed,mmsi)
    el = cur.fetchone()
    cur.close()
    print(el)
    return el

def warning(mmsi):
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



"""
with pyais.AISTracker() as tracker:
    tracker.register_callback(AISTrackEvent.CREATED, handle_create)

    tracker.register_callback(AISTrackEvent.UPDATED, handle_update)
    tracker.register_callback(AISTrackEvent.DELETED, handle_delete)
"""

def do_track():
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
                        cur.execute(add_waypoint,data_ship)
                        conn.commit()
                        _cpa_tcpa[decoded_msg.mmsi]= cpa_tcpa(decoded_msg.speed, decoded_msg.lat, decoded_msg.lon, decoded_msg.course, 244030153, 0, jemgum_lat,jemgum_lon, 180)
                elif (decoded_msg.msg_type == 5) :
                    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
                    data_ship = (decoded_msg.mmsi, decoded_msg.imo, decoded_msg.callsign, decoded_msg.shipname,decoded_msg.ship_type, decoded_msg.to_bow, decoded_msg.to_stern, decoded_msg.to_port, decoded_msg.to_starboard,  lt)
                    cur.execute(add_ship,data_ship)
                    conn.commit()
                elif (decoded_msg.msg_type == 24) :
                    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
                    if (decoded_msg.partno == 0):
                        data_ship = (decoded_msg.mmsi, decoded_msg.shipname, lt)
                        cur.execute(add_ship_24,data_ship)
                        conn.commit()
                    elif (decoded_msg.partno == 1):
                        data_ship = (decoded_msg.callsign, decoded_msg.ship_type, decoded_msg.to_bow, decoded_msg.to_stern, decoded_msg.to_port, decoded_msg.to_starboard, decoded_msg.mmsi)
                        cur.execute(update_ship_24,data_ship)
                        conn.commit()
                #tracker.update(msg)
                #latest_tracks = tracker.n_latest_tracks(10)
            except UnknownMessageException as e:
                print(e)


t1 = Thread(target=do_track,)
t1.start()

def ship_type(n):
    return str(n)+" unavailable"

def show():
    #gc.set_debug(gc.DEBUG_LEAK)
    while True:
        #t.sleep(60)
        cur = conn.cursor()
        cur.execute(report)
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
            except Exception as e:
                print(e)
        t.sleep(10)
        cur.close()
        print("_________________________________________________________________________________________________________________________")
        n = gc.collect()
        print(n)


t2 = Thread(target= show)
#t2.start()

t1.join()

cur.close()
conn.close()
print(gc.garbage)
