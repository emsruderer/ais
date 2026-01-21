# SQL Statements
CREATE_TYPE_TABLE = """
    CREATE TABLE IF NOT EXISTS Shipstypes (
        ind  TINYINT(3) UNIQUE NOT NULL,
        soort  VARCHAR(51),
        PRIMARY KEY (ind)
    );
"""

CREATE_WARN_TABLE = """
CREATE TABLE IF NOT EXISTS Warnings (
    mmsi  INT(10) UNIQUE NOT NULL,
    callsign CHAR(7),
    name VARCHAR(20),
    type TINYINT(3),
    speed  FLOAT(4,1),
    lat  FLOAT(10,6),
    lon  FLOAT(10,6),
    course   FLOAT(4,1),
    repeats  TINYINT,
    time  TIMESTAMP,
    PRIMARY KEY (mmsi)
);
"""

CREATE_SHIPS_TABLE = """
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

CREATE_TRACK_TABLE = """
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

CREATE_CPA_TABLE = """
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


ADD_SHIP_TYPE = """ INSERT IGNORE INTO Shipstypes (ind,soort) VALUES (%s,%s); """

ADD_WARNING = """INSERT IGNORE INTO Warnings (mmsi,callsign,name,type,speed,lat,lon,course,repeats,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); """

ADD_CPA = ("""INSERT IGNORE INTO Cpa (mmsi,speed,lat,lon,course,heading,cpa,tcpa,last_updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """)

ADD_SHIP = ("""INSERT IGNORE INTO Ships (mmsi,imo,callsign,name,type,to_bow,to_stern,to_port,to_starboard, last_updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """)

ADD_SHIP_24 = ("""INSERT IGNORE INTO Ships (mmsi, name, last_updated) VALUES (%s,%s,%s) """)

UPDATE_CPA = ("""UPDATE IGNORE INTO Cpa (mmsi,speed,lat,lon,course,heading,cpa,tcpa,last_updated) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """)

UPDATE_SHIP = ("UPDATE Ships " "SET imo=%s, callsign=%s, name=%s, type=%s, to_bow = %s, to_stern =%s, to_port =%s, to_starboard=%s,last_updated=%s WHERE mmsi = %s")

UPDATE_SHIP_24 = ("UPDATE IGNORE Ships " "SET callsign=%s, type=%s, to_bow = %s, to_stern =%s, to_port =%s, to_starboard=%s WHERE mmsi = %s")

ADD_WAYPOINT = ("INSERT IGNORE INTO Tracks" "(mmsi,speed,lat,lon,course,heading,time)" "VALUES (%s,%s,%s,%s,%s,%s, %s);")

REPORT = ("SELECT Tracks.mmsi, Tracks.time, MAX(Tracks.speed), Tracks.lat, Tracks.lon, Tracks.course, Tracks.heading, Ships.name, Ships.callsign, Ships.type FROM Tracks LEFT JOIN Ships ON Tracks.mmsi = Ships.mmsi GROUP BY Tracks.mmsi ORDER BY Tracks.time ;")

SHIP_DATA = ("SELECT Tracks.mmsi, Tracks.time, MAX(Tracks.speed), Tracks.lat, Tracks.lon, Tracks.course, Tracks.heading, Ships.name, Ships.callsign, Ships.type FROM Tracks LEFT JOIN Ships ON Tracks.mmsi = Ships.mmsi WHERE Tracks.mmsi = %s ;")

ROMP_SPEED = ("SELECT SQRT(to_bow + to_stern)*2.42 as rump_speed FROM Ships WHERE mmsi = %s")

def read_textfile():
    """ read shiptype.txt and create dict """
    with open('shiptype.txt', encoding="utf-8") as f:
        all_text= f.read()
        lines = all_text.splitlines()
        ship_type = dict()
        for line in lines:
            tup = line.partition('\t')
            ship_type[tup[0]] = tup[2]

    print('{')
    for sleutel, ship in ship_type.items():
        print(sleutel,':  "'+ ship+'",')
    print('}')
    return ship_type


if __name__ == "__main__":
    import mysql.connector
    import sys

    # Connect to MariaDB Platform
    try :
        conn = mysql.connector.connect(
            user="nanno",
            password="11082004",
            host="localhost",
            port=3306,
            database="db_ais"
        )
    except ConnectionError as e:
        print(f"Error connecting to MariaDB Platform  {e}")
        sys.exit(1)

    cur = conn.cursor()

    print("Connected")
    conn.autocommit = True
    print(conn.autocommit)
    cur.execute(CREATE_TYPE_TABLE)
    cur.execute(CREATE_WARN_TABLE)
    cur.execute(CREATE_SHIPS_TABLE)
    cur.execute(CREATE_TRACK_TABLE)
    cur.execute(CREATE_CPA_TABLE)
    ship_types = read_textfile()
    for ind, soort in ship_types.items():
        cur.execute(ADD_SHIP_TYPE, (ind, soort))
    conn.close()
