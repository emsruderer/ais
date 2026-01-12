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

    type_of_ship = []
    for i in range(100):
        data = (i,shiptype(i))
        cur.execute(ADD_SHIP_TYPE,data)
        print(shiptype(i))
    conn.close()
