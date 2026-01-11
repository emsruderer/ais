# Module Imports
import sys
import pyais
from pyais.stream import TCPConnection
#from pyais.tracker import AISTrackEvent
from pyais.exceptions import UnknownMessageException
import time as t
import datetime
from threading import Thread
from pyais.filter import haversine
import gc
import mysql.connector
from speech import call_ship
from shipstype import shiptype
from aisgpio import marifoon_on, marifoon_off

ais_watch = 'ais-watch.fritz.box'
port = 10110
jemgum_lat = 53.26417
jemgum_lon = 7.396137
# 53.2641733575126° , 7.396137714385986°
jemgum = (jemgum_lat,jemgum_lon)
# 53.269537800047864° , 7.396695613861085°
north_border = (53.27338,7.74899) 
south_border = (53.25540, 7.394914627075195)
#53.27127019153723° , 7.397489547729492°

print(haversine(jemgum,north_border))
print(haversine(jemgum,south_border))

# Connect to MariaDB Platform
try :
    conn = mysql.connector.connect(
        user="nanno",       
        password="11082004",
        host=ais_watch,
        port=3306,
        database="ais"
    )
    
except mariadb.Error as e: 
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

create_warn_table = """
        CREATE TABLE IF NOT EXISTS Warnings (
            mmsi  INT(10) UNIQUE NOT NULL,
            callsign CHAR(7),
            name VARCHAR(20),
            type TINYINT(3),
            speed  FLOAT(4,1),
            lat  FLOAT(10,6),
            lon  FLOAT(10,6),
            course   FLOAT(4,1),
            repeats  SMALLINT,
            time  TIMESTAMP,
            PRIMARY KEY (mmsi)
        );  
    """

add_warning = ("""INSERT IGNORE INTO Warnings (mmsi,callsign,name,type,speed,lat,lon,course,repeats,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """)
    

add_ship = ("""INSERT IGNORE INTO Ships (mmsi,imo,callsign,name,type,to_bow,to_stern,to_port,to_starboard, last_updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """)

add_ship_24 = ("""INSERT IGNORE INTO Ships (mmsi, name, last_updated) VALUES (%s,%s,%s) """)

update_ship = ("UPDATE Ships " "SET imo=%s, callsign=%s, name=%s, type=%s, to_bow = %s, to_stern =%s, to_port =%s, to_starboard=%s,last_updated=%s WHERE mmsi = %s")

update_ship_24 = ("UPDATE IGNORE Ships " "SET callsign=%s, type=%s, to_bow = %s, to_stern =%s, to_port =%s, to_starboard=%s WHERE mmsi = %s")

add_waypoint = ("INSERT IGNORE INTO Tracks" "(mmsi,speed,lat,lon,course,heading,time)" "VALUES (%s,%s,%s,%s,%s,%s, %s);")

report = ("SELECT Tracks.mmsi, Tracks.time, MAX(Tracks.speed), Tracks.lat, Tracks.lon, Tracks.course, Tracks.heading, Ships.name, Ships.callsign, Ships.type FROM Tracks LEFT JOIN Ships ON Tracks.mmsi = Ships.mmsi GROUP BY Tracks.mmsi ORDER BY Tracks.time ;")

ship_data = ("SELECT Tracks.mmsi, Tracks.time, MAX(Tracks.speed), Tracks.lat, Tracks.lon, Tracks.course, Tracks.heading, Ships.name, Ships.callsign, Ships.type FROM Tracks LEFT JOIN Ships ON Tracks.mmsi = Ships.mmsi WHERE Tracks.mmsi = %s ;")

add_warning = ("""INSERT IGNORE INTO Warnings (mmsi,callsign,name,type,speed,lat,lon,course,repeats,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE repeats= %s""")

romp_speed = ("SELECT SQRT(to_bow + to_stern)*2.42 as rump_speed FROM Ships WHERE mmsi = %s")
"""
DROP VIEW speedpoint;
CREATE VIEW speedpoint AS SELECT mmsi, MAX(speed) as Speed, lat,lon, course, time FROM Tracks GROUP BY mmsi ORDER BY time;
select * from speedpoint;

SELECT speedpoint.mmsi, speedpoint.Speed, speedpoint.time, Ships.name, Ships.callsign, Ships.type FROM speedpoint LEFT JOIN Ships ON speedpoint.mmsi = Ships.mmsi ORDER BY speedpoint.time;
"""
#lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
cur.execute(create_ships_table)
cur.execute(create_track_table)
cur.execute(create_warn_table)

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

def in_range(lat,lon):
    if (lat and lon):
        distance = haversine((jemgum_lat,jemgum_lon), (lat,lon))
        return distance <= 0.5
    else:
        return False

def romp_snelheid(mmsi):
    cur = conn.cursor()
    cur.execute(romp_speed,mmsi)
    el = cur.fetchone()
    cur.close()
    print(el)
    return el[0]

enabled = True

def warning(mmsi):
    cur = conn.cursor()
    cur.execute(ship_data,[mmsi])
    ship= cur.fetchone()
    cur.close()
    try:
        mmsi = ship[0]
        time = ship[1]
        speed = ship[2]
        lat = ship[3]
        lon = ship[4].asdict()
        course = ship[5] 
        heading = ship[6]
        name= ship[7]
        callsign = ship[8]
        typ = ship[9]
        s = F"{mmsi:n} {time} {speed:5.1f} {lat:8.4f} {lon:8.4f} {course:6.1f} {heading:6.1f} {name:24} {callsign:8} {shiptype(typ)}"
        repeats = 1
        data_ship = (mmsi,callsign,name,typ,speed,lat,lon,course,repeats,time,3)
        cur = conn.cursor()
        cur.execute(add_warning, data_ship)
        cur.close()
        if enabled:
            call_ship(mmsi,name,callsign)
    except Exception as e:
        print(e)
    


"""
with pyais.AISTracker() as tracker:
    tracker.register_callback(AISTrackEvent.CREATED, handle_create)

    tracker.register_callback(AISTrackEvent.UPDATED, handle_update)
    tracker.register_callback(AISTrackEvent.DELETED, handle_delete)
"""    

def do_track():
    cur = conn.cursor()
    for msg in TCPConnection(ais_watch, port=port):
        global latest_tracks
        try:
            decoded_msg = msg.decode()
            if (decoded_msg.msg_type in [1,2,3,18]) :
                if in_range(decoded_msg.lat,decoded_msg.lon) and decoded_msg.speed > 0.5 and decoded_msg.speed < 102.3:
                    lt = datetime.datetime.fromtimestamp(t.time()).strftime('%Y-%m-%d %H:%M:%S')
                    data_ship = (decoded_msg.mmsi, decoded_msg.speed, decoded_msg.lat, decoded_msg.lon, decoded_msg.course, decoded_msg.heading, lt )
                    cur.execute(add_waypoint,data_ship)
                    conn.commit()
                    rs = romp_snelheid([decoded_msg.mmsi])
                    if  rs < decoded_msg.speed:
                         #print('snelheid >  bn rompsnelheid  (', decoded_msg.speed, '>',rs,')')
                         warning(decoded_msg.mmsi)
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
                if (decoded_msg.partno == 1):
                    data_ship = (decoded_msg.callsign, decoded_msg.ship_type, decoded_msg.to_bow, decoded_msg.to_stern, decoded_msg.to_port, decoded_msg.to_starboard, decoded_msg.mmsi)
                    cur.execute(update_ship_24,data_ship)
                    conn.commit()
            #tracker.update(msg)
            #latest_tracks = tracker.n_latest_tracks(10)
        except UnknownMessageException as e:
            print(e)
           
# print('rompsnelheid:',romp_snelheid([244030153]))
     

t1 = Thread(target=do_track,)

def monitor():
    global enabled
    emstraffic_interrupt = 40
    while True:
        minute = datetime.datetime.now().minute
        if minute > emstraffic_interrupt and minute < emstraffic_interrupt + 4:
            enabled = False
        else:
            enabled = True
        t.sleep(20)   
    
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
                s = F"{mmsi:n} {time} {speed:5.1f} {lat:8.4f} {lon:8.4f} {course:6.1f} {heading:6.1f} {name:24} {callsign:8} {shiptype(typ)}"
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

#warning(244030153)

t2 = Thread(target= monitor)
t1.start()
t2.start()
t1.join()


cur.close()
conn.close()
#print(gc.garbage)
