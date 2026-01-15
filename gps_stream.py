"""gps stream from signalk"""

from socket import socket, AF_INET, SOCK_STREAM
import json

def decode_gll(vggll:str) -> dict:
    """Decode GLL NMEA sentence into a dictionary."""
    fields = vggll.split(',')
    if len(fields) < 7:
        raise ValueError("Invalid GLL sentence")
    lat = float(fields[1][:2]) + float(fields[1][2:]) / 60.0
    if fields[2] == 'S':
        lat = -lat

    lon = float(fields[3][:3]) + float(fields[3][3:]) / 60.0
    if fields[4] == 'W':
        lon = -lon

    time_utc = fields[5]
    status = fields[6]

    return {
        'latitude': lat,
        'longitude': lon,
        'time_utc': time_utc,
        'status': status
    }


def decode_vts(gpvtg:str) -> dict:
    """Decode VTG NMEA sentence into a dictionary."""
    fields = gpvtg.split(',')
    if len(fields) < 9:
        raise ValueError("Invalid VTG sentence")
    if fields[1] == '':
        true_track = None
        magnetic_track = None
        speed_knots = None
        speed_kmh = None
    else:
        true_track = float(fields[1])
        magnetic_track = float(fields[3])
        speed_knots = float(fields[5])
        speed_kmh = float(fields[7])
    return {
        'true_track': true_track,
        'magnetic_track': magnetic_track,
        'speed_knots': speed_knots,
        'speed_kmh': speed_kmh
    }

def decode_zda(gpzda:str) -> dict:
    """Decode ZDA NMEA sentence into a dictionary."""
    fields = gpzda.split(',')
    if len(fields) < 5:
        raise ValueError("Invalid ZDA sentence")
    time_utc = fields[1]
    day = int(fields[2])
    month = int(fields[3])
    year = int(fields[4])
    return {
        'time_utc': time_utc,
        'day': day,
        'month': month,
        'year': year
    }

def decode_hdt(gphdt:str) -> dict:
    """Decode HDT NMEA sentence into a dictionary."""
    fields = gphdt.split(',')
    if len(fields) < 2:
        raise ValueError("Invalid HDT sentence")
    heading = float(fields[1])
    return {
        'heading': heading
    }

def decode_rmc(gprmc:str) -> dict:
    """Decode RMC NMEA sentence into a dictionary."""
    fields = gprmc.split(',')
    if len(fields) < 12:
        raise ValueError("Invalid RMC sentence")
    time_utc = fields[1]
    status = fields[2]
    lat = float(fields[3][:2]) + float(fields[3][2:]) / 60.0
    if fields[4] == 'S':
        lat = -lat

    lon = float(fields[5][:3]) + float(fields[5][3:]) / 60.0
    if fields[6] == 'W':
        lon = -lon

    speed_over_ground = float(fields[7])
    course_over_ground = float(fields[8])
    date = fields[9]

    return {
        'time_utc': time_utc,
        'status': status,
        'latitude': lat,
        'longitude': lon,
        'speed_over_ground': speed_over_ground,
        'course_over_ground': course_over_ground,
        'date': date
    }


def gps_from_signalk(host='localhost', port=10110):
    """Generator that yields GPS data from a SignalK server."""
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((host, port))
        buffer = ""
        while True:
            data = s.recv(4096).decode('utf-8')

            if not data:
                break
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if line.startswith("$GRMC"):
                     yield line
                elif line.startswith("$GPGLL"):
                    data = decode_gll(line)
                    yield data
                elif line.startswith("$GPRMC"):
                    yield line
                elif line.startswith("$GPVTG"):
                    data = decode_vts(line)
                    yield data
                elif line.startswith("$GPZDA"):
                    data = decode_zda(line)
                    yield data
                elif line.startswith("$GPHDT"):
                    data = decode_hdt(line)
                    yield data

if __name__ == "__main__":
    for gps in gps_from_signalk():
        print(gps)
        """gps stream from signalk"""