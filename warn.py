"""
Talking AIS watcher
"""
import dataclasses
import math
from re import VERBOSE
from attr import attr
from pyais.filter import haversine
from cpa_tracker import CPATrack
from speech import speak, str_number
from nationality import get_country


HOST = 'localhost'
PORT = 10110
SILENT = False
VERBOSE = True

JEMGUM_LAT = 53.26379
JEMGUM_LON = 7.39738

def nationaliteit(mmsi):
    """
    nationaliteit based on mmsi
    """
    return get_country(mmsi)[1] + " "

def bearing(lat1,lon1,lat2,lon2):
    """Calculate bearing between two lat/lon points in degrees"""
    if lat1 is not None and lon1 is not None:
        lat1,lon1 = math.radians(lat1), math.radians(lon1)
        lat2,lon2 = math.radians(lat2), math.radians(lon2)

        d_lon = lon2 - lon1

        y = math.sin(d_lon) * math.cos(lat2)
        x = math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(d_lon)

        direction_rad = math.atan2(y,x)
        direction_deg = math.degrees(direction_rad)

        return int((direction_deg+360)%360)
    else:
        return 0

def distance(lat,lon,lat2,lon2):
    """Calculate distance between two lat/lon points in nautical miles"""
    if lat is not None and lon is not None:
        return haversine((lat2,lon2), (lat,lon))*1.854
    else:
        return 0.0

FIELDS = dataclasses.fields(CPATrack)

def nm_to_meters(nm):
    """Convert nautical miles to meters if less than 1 nM, otherwise no change."""
    if nm < 1.0:
        return nm * 1854, True
    return nm, False

def hr_to_min(hr):
    """Convert hours to minutes."""
    if hr < 1.0:
        return hr * 60, True
    return hr, False

def do_warn(que, my_ship=None):
    """ do warning based on ais tracks """
    while True:
        msg = que.get()
        if VERBOSE:
            print("Warn got message:", msg)
        mmsi = 0
        shipname = "onbekend"
        imo = 0
        callsign = "onbekend"
        course = 0.0
        distance = 0.0
        bearing = 0.0
        cpa = 0.0
        tcpa = 0.0
        bericht = ""
        for field in FIELDS:
            print(f"Field: {field.name}")
            print(f"Type: {field.type}")
            print(f"Value: {getattr(msg, field.name)}")
            print(f"Default: {field.default}")
            print("-" * 20)

            if field.name == "mmsi":
                mmsi = getattr(msg, field.name)
                #bericht += "MMSI " + str_number(mmsi) + " "
                bericht = "Naderend " + nationaliteit(mmsi) + "schip, "
            elif field.name == "shipname":
                shipname = getattr(msg, field.name)
                if shipname is not None:
                    bericht += " " + shipname + ","
            elif field.name == "callsign":
                callsign = getattr(msg, field.name)
                if callsign is not None:
                    bericht += "en Roepnaam " + callsign + " "
            elif field.name == "course":
                course = getattr(msg, field.name)
                bericht += "op koers " + str_number(int(course)) + " graden, "
            elif field.name == "speed":
                bericht += "met " + str_number(int(getattr(msg, field.name))) + " knopen, "
            elif field.name == "heading":
                heading = getattr(msg, field.name)
                bericht += "met heading " + str_number(int(heading)) + " graden, "
            elif field.name == "ship_type":
                print("Ship type:", getattr(msg, field.name))
            elif field.name == "destination":
                print("Destination:", getattr(msg, field.name))
            elif field.name == "last_updated":
                print("Last updated:", getattr(msg, field.name))
            elif field.name == "status":
                print("Status:", getattr(msg, field.name))
            elif field.name == "turn":
                print("Turn:", getattr(msg, field.name))
            elif field.name == "distance":
                distance = getattr(msg, field.name)
                distance, waar = nm_to_meters(distance)
                if waar:
                    maat = " meter"
                else:
                    maat = " mijl"
                bericht += "nu op  " + str_number(int(distance)) + maat + " van ons vandaan"
            elif field.name == "bearing":
                bearing = getattr(msg, field.name)
                bericht += " in richting " + str_number(int(bearing)) + ", "
            elif field.name == "cpa":
                cpa = getattr(msg, field.name)
                cpa, waar = nm_to_meters(cpa)
                if waar:
                    maat = " meter,"
                else:
                    maat = " mijl,"
                bericht += "kleinste afstand " + str_number(int(cpa)) + maat
            elif field.name == "tcpa":
                tcpa = getattr(msg, field.name)
                tcpa, waar = hr_to_min(tcpa)
                if waar:
                    maat = " minuten, "
                else:
                    maat = " uur, "
                bericht += "over " + str_number(int(tcpa)) + maat

        if isinstance(msg, CPATrack) :
            warning = "Waarschuwing!,"  + bericht
            if VERBOSE:
                print(warning)

            if not SILENT:
                speak(warning)
    que.task_done()

if __name__ == '__main__':
   print("hr_to_min(0.5) =", hr_to_min(0.5) )