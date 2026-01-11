""" create shiptypes table via dict """

def shiptype(t : int):
    ship_type =	{
                0 :  "Not available",
                1 :  "Reserved for future use",
                2 :  "Reserved for future use",
                3 :  "Reserved for future use",
                4 :  "Reserved for future use",
                5 :  "Reserved for future use",
                6 :  "Reserved for future use",
                7 :  "Reserved for future use",
                8 :  "Reserved for future use",
                9 :  "Reserved for future use",
                10 :  "Reserved for future use",
                11 :  "Reserved for future use",
                12 :  "Reserved for future use",
                13 :  "Reserved for future use",
                14 :  "Reserved for future use",
                15 :  "Reserved for future use",
                16 :  "Reserved for future use",
                17 :  "Reserved for future use",
                18 :  "Reserved for future use",
                19 :  "Reserved for future use",
                20  :  "Wing in ground (WIG)", #all ships of this type",
                21  :  "Wing in ground (WIG), Hazardous category A",
                22 :  "Wing in ground (WIG), Hazardous category B",
                23 :  "Wing in ground (WIG), Hazardous category C",
                24 :  "Wing in ground (WIG), Hazardous category D",
                25 :  "Wing in ground (WIG), Reserved for future use",
                26 :  "Wing in ground (WIG), Reserved for future use",
                27 :  "Wing in ground (WIG), Reserved for future use",
                28 :  "Wing in ground (WIG), Reserved for future use",
                29 :  "Wing in ground (WIG), Reserved for future use",
                30 :  "Fishing",
                31 :  "Towing",
                32 :  "Towing: length exceeds 200m or breadth exceeds 25m",
                33 :  "Dredging or underwater ops",
                34 :  "Diving ops",
                35 :  "Military ops",
                36 :  "Sailing",
                37 :  "Pleasure Craft",
                38 :  "Reserved",
                39 :  "Reserved",
                40 :  "High speed craft (HSC)", #all ships of this type",
                41 :  "High speed craft (HSC), Hazardous category A",
                42 :  "High speed craft (HSC), Hazardous category B",
                43 :  "High speed craft (HSC), Hazardous category C",
                44 :  "High speed craft (HSC), Hazardous category D",
                45 :  "High speed craft (HSC), Reserved for future use",
                46 :  "High speed craft (HSC), Reserved for future use",
                47 :  "High speed craft (HSC), Reserved for future use",
                48 :  "High speed craft (HSC), Reserved for future use",
                49 :  "High speed craft (HSC)", # No additional information",
                50 :  "Pilot Vessel",
                51 :  "Search and Rescue vessel",
                52 :  "Tug",
                53 :  "Port Tender",
                54 :  "Anti-pollution equipment",
                55 :  "Law Enforcement",
                56 :  "Spare - Local Vessel",
                57 :  "Spare - Local Vessel",
                58 :  "Medical Transport",
                59 :  "Noncombatant ship according to RR Resolution No. 18",
                60 :  "Passenger", #all ships of this type",
                61 :  "Passenger, Hazardous category A",
                62 :  "Passenger, Hazardous category B",
                63 :  "Passenger, Hazardous category C",
                64 :  "Passenger, Hazardous category D",
                65 :  "Passenger, Reserved for future use",
                66 :  "Passenger, Reserved for future use",
                67 :  "Passenger, Reserved for future use",
                68 :  "Passenger, Reserved for future use",
                69 :  "Passenger", #No additional information",
                70 :  "Cargo", #, all ships of this type",
                71 :  "Cargo, Hazardous category A",
                72 :  "Cargo, Hazardous category B",
                73 :  "Cargo, Hazardous category C",
                74 :  "Cargo, Hazardous category D",
                75 :  "Cargo, Reserved for future use",
                76 :  "Cargo, Reserved for future use",
                77 :  "Cargo, Reserved for future use",
                78 :  "Cargo, Reserved for future use",
                79 :  "Cargo", #, No additional information",
                80 :  "Tanker", #all ships of this type",
                81 :  "Tanker, Hazardous category A",
                82 :  "Tanker, Hazardous category B",
                83 :  "Tanker, Hazardous category C",
                84 :  "Tanker, Hazardous category D",
                85 :  "Tanker, Reserved for future use",
                86 :  "Tanker, Reserved for future use",
                87 :  "Tanker, Reserved for future use",
                88 :  "Tanker, Reserved for future use",
                89 :  "Tanker", #, No additional information",
                90 :  "Other Type", #, all ships of this type",
                91 :  "Other Type, Hazardous category A",
                92 :  "Other Type, Hazardous category B",
                93 :  "Other Type, Hazardous category C",
                94 :  "Other Type, Hazardous category D",
                95 :  "Other Type, Reserved for future use",
                96 :  "Other Type, Reserved for future use",
                97 :  "Other Type, Reserved for future use",
                98 :  "Other Type, Reserved for future use",
                99 :  "Other Type", #, no additional information"
            }
    return ship_type[t]

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

ADD_SHIP_TYPE = """ INSERT IGNORE INTO Shipstypes (ind,soort) VALUES (%s,%s); """

ADD_WARNING = """INSERT IGNORE INTO Warnings (mmsi,callsign,name,type,speed,lat,lon,course,repeats,time) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s); """


def read_textfile():
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


if __name__ == "__main__":
    import mysql.connector
    import sys

    # Connect to MariaDB Platform
    try :
        conn = mysql.connector.connect(
            user="nanno",
            password="11082004",
            host="localhost", #'ais-watch.fritz.box'
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

    for i in range(100):
        data = (i,shiptype(i))
        cur.execute(ADD_SHIP_TYPE,data)
        print(shiptype(i))
